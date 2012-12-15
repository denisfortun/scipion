#!/usr/bin/env xmipp_python
#------------------------------------------------------------------------------------------------
#
# General script for Xmipp-based pre-processing of single-particles: 

# Author: Carlos Oscar, August 2011
#
from protlib_base import *
from xmipp import MetaData, MDL_SAMPLINGRATE, MDL_IMAGE, MDL_ZSCORE
import os
from os.path import exists, split, splitext
from protlib_utils import runJob, runShowJ
from protlib_filesystem import deleteFile,linkAcquisitionInfo, moveFile, removeBasenameExt
import glob
from protlib_gui_ext import showError

class ProtPreprocessParticles(XmippProtocol):
    def __init__(self, scriptname, project):
        XmippProtocol.__init__(self, protDict.preprocess_particles.name, scriptname, project)
        self.Import = 'from protocol_preprocess_particles import *'
        (self.InputDir,file)=split(self.InSelFile)
        baseFile = removeBasenameExt(file)
        self.OutStack = self.getFilename('images_stk')
        self.OutMetadata = self.getFilename('images')
        self.TiltPair = exists(getProtocolFilename('tilted_pairs', WorkingDir=self.InputDir))

    def defineSteps(self):
        self.insertStep('copyImages',verifyfiles=[self.OutMetadata, self.OutStack],
                           InputFile=self.InSelFile, OutputStack=self.OutStack,
                           OutputMetadata=self.OutMetadata)
        self.insertStep('createAcquisition',InputFile=self.InSelFile, WorkingDir=self.WorkingDir,
                        DoResize=self.DoResize, NewSize=self.NewSize)
        # Apply filters if selected
        if self.DoFourier:
            self.insertStep('runFourierFilter',stack=self.OutStack,freq_low=self.Freq_low,freq_high=self.Freq_high,freq_decay=self.Freq_decay,Nproc=self.NumberOfMpi)
        if self.DoGaussian:
            self.insertStep('runGaussianFilter',stack=self.OutStack,freq_sigma=self.Freq_sigma, Nproc=self.NumberOfMpi)
            
        # Apply mask
        if self.DoMask:
            if self.Substitute == "value":
                self.Substitute = str(self.SubstituteValue)
            params = "-i %s --substitute %s --mask %s " % (self.OutStack, self.Substitute, self.MaskType)
            if self.MaskType == 'raised_cosine':
                params += "-%d -%d" % (self.MaskRadius, self.MaskRadius + self.MaskRadiusOuter)
            elif self.MaskType == 'circular':
                params += '-%d' % self.MaskRadius
            else: # from file:
                params += self.MaskFile
            self.insertRunJobStep("xmipp_transform_mask", params)
            
        # Resize images
        if self.DoCrop:
            self.insertStep('runCrop',stack=self.OutStack, cropSize=self.CropSize, tmpStack=self.tmpPath('tmpCrop.stk'))
        if self.DoResize:
            self.insertStep('runResize',stack=self.OutStack,new_size=self.NewSize,Nproc=self.NumberOfMpi)
        
        if self.TiltPair:
            if self.InSelFile.find("_untilted")!=-1:
                fnBase=split(self.InSelFile)[1]
                fnFamily=fnBase.replace("_untilted","")
                self.insertStep('translateTiltPair',verifyfiles=[self.workingDirPath(fnFamily)],
                                   WorkingDir=self.WorkingDir,InputDir=self.InputDir,FnFamily=fnFamily,OutStack=self.OutStack)
                fnTilted=fnBase.replace("_untilted","_tilted")
                self.insertStep('copyFile',verifyfiles=[self.workingDirPath(fnTilted)],source=self.InSelFile.replace('_untilted','_tilted'),
                                   dest=self.workingDirPath(fnTilted))
                self.insertStep('copyFile',verifyfiles=[self.workingDirPath('tilted_pairs.xmd')],source=os.path.join(self.InputDir,'tilted_pairs.xmd'),
                                   dest=self.workingDirPath('tilted_pairs.xmd'))
        
    def validate(self):
        errors = []
        if self.DoResize:
            if self.NewSize < 1:
                errors.append("New size for scale have not correctly set")
            if self.TiltPair:
                errors.append("Cannot scale particles extracted from tilt pairs. Re-extract the particles at a different sampling rate, instead.")
            if self.DoCrop and self.OutputSize > self.NewSize:
                errors.append("Crop output size cannot be greater than resize output size")
        return errors

    def setStepMessage(self, stepMsg):
        step = len(self.messages) # assumed just one message before calling this function
        msg = "Step %d -> " % step
        msg += stepMsg % self.ParamsDict
        self.messages.append(msg)            
        
    def summary(self):
        self.messages = []
        self.messages.append("Input images: [%s]" % self.InSelFile)
        self.messages.append("Steps applied:")
        
        if self.DoFourier:
            self.setStepMessage("Fourier filter: freq_low = %(Freq_low)f freq_high = %(Freq_high)f freq_decay = %(Freq_decay)f")            
        if self.DoGaussian:
            self.setStepMessage("Gaussian filter: freq_sigma = %(Freq_sigma)f")
        
        if self.DoMask:
            self.setStepMessage("Mask: mask file = %(MaskFile)s substituted value = %(Substitute)s")
        self.messages.append("Output: [%s]" % self.OutMetadata)

        if self.DoResize:
            self.setStepMessage("Resize: NewSize = %(NewSize)d")            
        if self.DoCrop:
            self.setStepMessage("Crop: CropSize = %(CropSize)d")
        return self.messages

    def visualize(self):
        if not exists(self.OutStack):
            showError("Error", "There is no result yet")
        else:
            runShowJ(self.OutMetadata)

def createAcquisition(log,InputFile,WorkingDir,DoResize,NewSize):
    fnAcqIn = findAcquisitionInfo(InputFile)
    if not fnAcqIn is None:
        fnAcqOut = getProtocolFilename('acquisition', WorkingDir=WorkingDir)
              
        if not DoResize:
            createLink(log, fnAcqIn, fnAcqOut)
        else:    
            md = MetaData(fnAcqIn)
            id = md.firstObject()
            Ts = md.getValue(MDL_SAMPLINGRATE, id)
            (Xdim, Ydim, Zdim, Ndim) = xmipp.ImgSize(InputFile)
            downsampling = float(Xdim)/NewSize;
            md.setValue(MDL_SAMPLINGRATE,Ts*downsampling,id)
            md.write(getProtocolFilename('acquisition_info', WorkingDir=WorkingDir))

def copyImages(log,InputFile,OutputStack,OutputMetadata):
    runJob(log,"xmipp_image_convert","-i %(InputFile)s -o %(OutputStack)s" % locals())
    mDstack = MetaData(OutputStack)
    if xmipp.FileName.isMetaData(xmipp.FileName(InputFile)):
        mDin = MetaData(InputFile)
        mDin.removeDisabled()
        mDin.removeLabel(MDL_IMAGE)
        mDin.removeLabel(MDL_ZSCORE)
        mDaux = MetaData(mDin)
        mDstack.merge(mDaux)
    mDstack.write(OutputMetadata)

def translateTiltPair(log,WorkingDir,InputDir,FnFamily,OutStack):
    md = MetaData(OutStack)
    MDfamily=MetaData(os.path.join(InputDir,FnFamily))
    MDfamily.merge(md)
    MDfamily.write(os.path.join(WorkingDir,FnFamily))

