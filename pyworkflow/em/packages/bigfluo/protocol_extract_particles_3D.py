# **************************************************************************
# *
# * Authors:     Denis Fortun (denis.fortun@epfl.ch)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
"""
This sub-package contains the XmippProtExtractParticles protocol
"""

from glob import glob
from os.path import exists, basename

import pyworkflow.em.metadata as md
from pyworkflow.object import String, Float
from pyworkflow.em.packages.xmipp3.constants import SAME_AS_PICKING, OTHER, ORIGINAL
from pyworkflow.protocol.constants import STEPS_PARALLEL, LEVEL_ADVANCED, STATUS_FINISHED
from pyworkflow.protocol.params import (PointerParam, EnumParam, FloatParam, IntParam, 
                                        BooleanParam, RelationParam, Positive)
from pyworkflow.em.protocol import  ProtExtractParticles
from pyworkflow.em.data import SetOfVolumes
from pyworkflow.utils.path import removeBaseExt, replaceBaseExt
from pyworkflow.em.protocol import ProtInitialVolume

from pyworkflow.em.packages.xmipp3.convert import writeSetOfCoordinates, readSetOfVolumes
from xmipp3 import XmippProtocol

# Rejection method constants
REJECT_NONE = 0
REJECT_MAXZSCORE = 1
REJECT_PERCENTAGE = 2

                
class ProtExtractParticles3D(ProtExtractParticles, ProtInitialVolume, XmippProtocol):
    """Protocol to extract particles from a set of coordinates"""
    _label = 'extract particles 3D'
    
    def __init__(self, **args):
        ProtExtractParticles.__init__(self, **args)
        ProtInitialVolume.__init__(self, **args)
        self.stepsExecutionMode = STEPS_PARALLEL
        
    #--------------------------- DEFINE param functions --------------------------------------------   
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('inputVolumes', PointerParam, label="Input volumes", important=True, 
                      pointerClass='SetOfVolumes',# pointerCondition='hasRepresentatives',
                      help='Select the input volumess from the project.')  
        form.addParam('inputCoordinates', PointerParam, label="Coordinates", important=True,
                      pointerClass='SetOfCoordinates',
                      help='Select the SetOfCoordinates ')
        
        form.addParam('downsampleType', EnumParam, choices=['same as picking', 'other', 'original'], 
                      default=0, important=True, label='Downsampling type', display=EnumParam.DISPLAY_COMBO, 
                      help='Select the downsampling type.')
        form.addParam('downFactor', FloatParam, default=2, condition='downsampleType==1',
                      label='Downsampling factor',
                      help='This factor is always referred to the original sampling rate. '
                      'You may use independent downsampling factors for extracting the '
                      'particles, picking them and estimating the CTF. All downsampling '
                      'factors are always referred to the original sampling rate, and '
                      'the differences are correctly handled by Xmipp.')        

#         form.addParam('inputMicrographs', PointerParam, label="Micrographs", 
#                       condition='downsampleType != 0',
#                       pointerClass='SetOfMicrographs',
#                       help='Select the original SetOfMicrographs')

        form.addParam('boxSize', IntParam, default=0,
                      label='Particle box size', validators=[Positive],
                      help='In pixels. The box size is the size of the boxed particles, '
                      'actual particles may be smaller than this.')

        form.addParam('doSort', BooleanParam, default=True,
                      label='Perform sort by statistics',
                      help='Perform sort by statistics to add zscore info to particles.')

        form.addParam('rejectionMethod', EnumParam, choices=['None','MaxZscore', 'Percentage'],
                      default=REJECT_NONE, display=EnumParam.DISPLAY_COMBO, condition='doSort',
                      label='Automatic particle rejection',
                      help='How to automatically reject particles. It can be none (no rejection),'
                      ' maxZscore (reject a particle if its Zscore is larger than this value), '
                      'Percentage (reject a given percentage in each one of the screening criteria).',
                      expertLevel=LEVEL_ADVANCED)

        form.addParam('maxZscore', IntParam, default=3, expertLevel=LEVEL_ADVANCED,
                      condition='doSort and rejectionMethod==%d' % REJECT_MAXZSCORE,
                      label='Maximum Zscore',
                      help='Maximum Zscore above which particles are rejected.')
        
        form.addParam('percentage', IntParam, default=5, expertLevel=LEVEL_ADVANCED, 
                      condition='rejectionMethod==%d' % REJECT_PERCENTAGE,
                      label='Percentage (%)',
                      help='Percentage of particles to reject')
        
        form.addSection(label='Preprocess')
        form.addParam('doRemoveDust', BooleanParam, default=True, important=True,
                      label='Dust removal (Recommended)', 
                      help='Sets pixels with unusually large values to random values from a Gaussian '
                      'with zero-mean and unity-standard deviation.')
        form.addParam('thresholdDust', FloatParam, default=3.5, 
                      condition='doRemoveDust', expertLevel=LEVEL_ADVANCED,
                      label='Threshold for dust removal',
                      help='Pixels with a signal higher or lower than this value times the standard '
                      'deviation of the image will be affected. For cryo, 3.5 is a good value.'
                      'For high-contrast negative stain, the signal itself may be affected so '
                      'that a higher value may be preferable.')
        form.addParam('doInvert', BooleanParam, default=False,
                      label='Invert contrast', 
                      help='Invert the contrast if your particles are black over a white background.')
        
        form.addParam('doNormalize', BooleanParam, default=True,
                      label='Normalize (Recommended)', 
                      help='It subtract a ramp in the gray values and normalizes so that in the '
                      'background there is 0 mean and standard deviation 1.')
        form.addParam('normType', EnumParam, choices=['OldXmipp','NewXmipp','Ramp'], default=2, 
                      condition='doNormalize', expertLevel=LEVEL_ADVANCED,
                      display=EnumParam.DISPLAY_COMBO,
                      label='Normalization type', 
                      help='OldXmipp (mean(Image)=0, stddev(Image)=1).  \n  '
                           'NewXmipp (mean(background)=0, stddev(background)=1)  \n  '
                           'Ramp (subtract background+NewXmipp).  \n  ')
        form.addParam('backRadius', IntParam, default=-1, condition='doNormalize',
                      label='Background radius',
                      help='Pixels outside this circle are assumed to be noise and their stddev '
                      'is set to 1. Radius for background circle definition (in pix.). '
                      'If this value is 0, then half the box size is used.', 
                      expertLevel=LEVEL_ADVANCED)
        
        form.addParallelSection(threads=4, mpi=1)

    #--------------------------- INSERT steps functions --------------------------------------------  
    def _insertAllSteps(self):
        """for each micrograph insert the steps to preprocess it
        """
        self._defineBasicParams()
        # Write pos files for each micrograph
        firstStepId = self._insertFunctionStep('writePosFilesStep')
        
        # For each micrograph insert the steps
        #run in parallel
        deps = []
        
        for vol in self.inputVols:
            localDeps = [firstStepId]
            volumeToExtract = vol.getFileName()
            baseVolName = removeBaseExt(vol.getFileName())

            # If downsample type is 'other' perform a downsample
            downFactor = self.downFactor.get()
            if self.downsampleType == OTHER and abs(downFactor - 1.) > 0.0001:
                fnDownsampled = self._getTmpPath(baseVolName+"_downsampled.xmp")
                args = "-i %(volumeToExtract)s -o %(fnDownsampled)s --step %(downFactor)f --method fourier"
                localDeps = [self._insertRunJobStep("xmipp_transform_downsample", args % locals(),prerequisites=localDeps)]
                volumeToExtract = fnDownsampled
            # If remove dust 
            if self.doRemoveDust:
                fnNoDust = self._getTmpPath(baseVolName+"_noDust.xmp")
                thresholdDust = self.thresholdDust.get() #TODO: remove this extra variable
                args=" -i %(volumeToExtract)s -o %(fnNoDust)s --bad_pixels outliers %(thresholdDust)f"
                localDeps = [self._insertRunJobStep("xmipp_transform_filter", args % locals(),prerequisites=localDeps)]
                volumeToExtract = fnNoDust

                # Actually extract
            deps.append(self._insertFunctionStep('extractParticlesStep', vol.getObjId(), baseVolName,
                                               volumeToExtract, prerequisites=localDeps))
        # Insert step to create output objects
        metaDeps = self._insertFunctionStep('createMetadataVolumeStep', prerequisites=deps)
        # TODO: adapt to 3D
#         if self.doSort:
#             screenDep = self._insertFunctionStep('screenParticlesStep', prerequisites=[metaDeps])
#             finalDeps = [screenDep]
#         else:
#             finalDeps = [metaDeps]

        finalDeps = [metaDeps]
        self._insertFunctionStep('createOutputStep', prerequisites=finalDeps)

    #--------------------------- STEPS functions --------------------------------------------
    def writePosFilesStep(self):
        """ Write the pos file for each micrograph on metadata format. """
        #self.posFiles = writeSetOfCoordinates(self._getExtraPath(), self.inputCoords)
        writeSetOfCoordinates(self._getExtraPath(), self.inputCoords)
    
    def downsamplingStep(self):
        pass
    
    def extractParticlesStep(self, micId, baseMicName, micrographToExtract):
        """ Extract particles from one micrograph """
        outputRoot = str(self._getExtraPath(baseMicName))
        #fnPosFile = self.getConvertedInput('inputCoords').getMicrographCoordFile(micId)
        fnPosFile =  self._getExtraPath(baseMicName + "_average.pos")

        # If it has coordinates extract the particles      
        particlesMd = 'particles@%s' % fnPosFile
        
        boxSize = self.boxSize.get()
        #if fnPosFile is not None and xmipp.existsBlockInMetaDataFile(particlesMd):
        if exists(fnPosFile):
            args = "-i %(micrographToExtract)s --pos %(particlesMd)s -o %(outputRoot)s --Xdim %(boxSize)d --compensateZsampling" % locals()
            if self.downsampleType.get() != SAME_AS_PICKING:
                args += " --downsampling %f" % (self.samplingFinal/self.samplingInput)
            if self.doInvert:
                args += " --invert"
            self.runJob("xmipp_micrograph_fluor_scissor", args)
            # Normalize 
            # Problm with the normalization: adapt to 3D?
            if self.doNormalize:
                self.runNormalize(outputRoot + '.stk', self.normType.get(), self.backRadius.get())          
                               
            if self.downsampleType.get() == OTHER:
                selfile = outputRoot + ".xmd"
                mdSelFile = md.MetaData(selfile)
                downsamplingFactor = self.samplingFinal/self.samplingInput
                mdSelFile.operate("Xcoor=Xcoor*%f" % downsamplingFactor)
                mdSelFile.operate("Ycoor=Ycoor*%f" % downsamplingFactor)
                mdSelFile.write(selfile)
        else:
            self.warning(" The micrograph %s hasn't coordinate file! Maybe you picked over a subset of micrographs" % baseMicName)
                
    def runNormalize(self, stack, normType, bgRadius):
        program = "xmipp_transform_normalize"
        args = "-i %(stack)s "
        
        if bgRadius <= 0:
            particleSize = md.MetaDataInfo(stack)[0]
            bgRadius = int(particleSize/2)
        
        if normType=="OldXmipp":
            args += "--method OldXmipp"
        elif normType=="NewXmipp":
            args += "--method NewXmipp --background circle %(bgRadius)d"
        else:
            args += "--method Ramp --background circle %(bgRadius)d"
        self.runJob(program, args % locals())
    
    def createMetadataVolumeStep(self):
        #Create volumes.xmd metadata
        fnVolumes = self._getOutputVolMd()
        volsXmd = md.MetaData() 
#        posFiles = glob(self._getExtraPath('*.pos')) 
        volFiles = glob(self._getExtraPath('*.stk')) 
        for volFn in volFiles:
            xmdFn = self._getExtraPath(replaceBaseExt(volFn, "xmd"))
            if exists(xmdFn):
                mdFn = md.MetaData(xmdFn)
                mdPos = md.MetaData('particles@%s' % volFn)
                mdPos.merge(mdFn) 
                #imgSet.appendFromMd(mdPos)
                print(fnVolumes)
                volsXmd.unionAll(mdPos)
            else:
                self.warning("The coord file %s wasn't used to extract! Maybe you are extracting over a subset of micrographs" % basename(volFn))
        volsXmd.write(fnVolumes)
    
    def screenParticlesStep(self):
        # If selected run xmipp_image_sort_by_statistics to add zscore info to images.xmd
        fnVolumes = self._getOutputVolMd()
        args="-i %(fnVolumes)s --addToInput"
        if self.rejectionMethod == REJECT_MAXZSCORE:
            maxZscore = self.maxZscore.get()
            args += " --zcut " + str(maxZscore)
        elif self.rejectionMethod == REJECT_PERCENTAGE:
            percentage = self.percentage.get()
            args += " --percent " + str(percentage)
        
        self.runJob("xmipp_image_sort_by_statistics", args % locals())
    
    def createOutputStep(self):
        # Create the SetOfVolumes object on the database
        #volSet = XmippSetOfParticles(self._getPath('images.xmd'))
        
        fnVolumes = self._getOutputVolMd()
        # Create output SetOfVolumess
        volSet = self._createSetOfVolumes()
        volSet.copyInfo(self.inputVols)
        
        if self.downsampleType == OTHER:
            volSet.setSamplingRate(self.inputVols.getSamplingRate()*self.downFactor.get())
#         volSet.setCoordinates(self.inputCoords)
        
        # Create a temporary set to read from the metadata file
        # and later create the good one with the coordinates 
        # properly set. We need this because the .update is not
        # working in the mapper when new attributes are added.
        auxSet = SetOfVolumes(filename=':memory:')
        auxSet.copyInfo(volSet)
        readSetOfVolumes(fnVolumes, auxSet)
        
        if self.downsampleType != SAME_AS_PICKING:
            factor = self.samplingInput / self.samplingFinal
        # For each particle retrieve micId from SetOFCoordinates and set it on the CTFModel
        for vol in auxSet:
            #FIXME: This can be slow to make a query to grab the coord, maybe use zip(volSet, coordSet)???
            coord = self.inputCoords[vol.getObjId()]
            if self.downsampleType != SAME_AS_PICKING:
                x, y = coord.getPosition()
                coord.setPosition(x*factor, y*factor)           
#             vol.setMicId(coord.getMicId())
#             vol.setCoordinate(coord)
            volSet.append(vol)
            
        self._storeMethodsInfo(fnVolumes)
        self._defineOutputs(outputVolumes=volSet)
        self._defineSourceRelation(self.inputCoordinates, volSet)
    
    #--------------------------- INFO functions -------------------------------------------- 
    def _validate(self):
        validateMsgs = []
        # doFlip can only be True if CTF information is available on picked micrographs
        return validateMsgs
    
    def _citations(self):
        return ['Vargas2013b']
        
    def _summary(self):
        downsampleTypeText = {
                              ORIGINAL:'Original micrographs',
                              SAME_AS_PICKING:'Same as picking',
                              OTHER: 'Other downsampling factor'}
        summary = []
        summary.append("Downsample type: %s" % downsampleTypeText.get(self.downsampleType.get()))
        if self.downsampleType == OTHER:
            summary.append("Downsampling factor: %.2f" % self.downFactor)
        summary.append("Particle box size: %d" % self.boxSize)
        
        if not hasattr(self, 'outputParticles'):
            summary.append("Output images not ready yet.") 
        else:
            summary.append("Particles extracted: %d" % (self.outputParticles.getSize()))
            
        return summary
    
    def _methods(self):
        methodsMsgs = []

        if self.getStatus() == STATUS_FINISHED:
            msg = "A total of %d particles of size %d were extracted" % (self.getOutput().getSize(), self.boxSize)

            if self.downsampleType == ORIGINAL:
                msg += " from original micrographs."

            if self.downsampleType == OTHER:
                msg += " from original micrographs with downsampling factor of %.2f." % self.downFactor

            if self.downsampleType == SAME_AS_PICKING:
                msg += "."

            msg += self.methodsVar.get('')

            methodsMsgs.append(msg)

            if self.doInvert:
                methodsMsgs.append("Inverted contrast on images.")

            if self.doNormalize.get():
                methodsMsgs.append("Normalization performed of type %s." % (self.getEnumText('normType')))

            if self.doRemoveDust.get():
                methodsMsgs.append("Removed dust over a threshold of %s." % (self.thresholdDust))

        return methodsMsgs

    #--------------------------- UTILS functions --------------------------------------------
    def _defineBasicParams(self):
        # Set sampling rate and inputMics according to downsample type
        self.inputCoords = self.inputCoordinates.get() 
        self.samplingInput = self.inputCoords.getMicrographs().getSamplingRate()
        self.inputVols = self.inputVolumes.get()
        
        if self.downsampleType.get() == SAME_AS_PICKING:
            # If 'same as picking' get samplingRate from input micrographs
            self.inputMics = self.inputCoords.getMicrographs()
            self.samplingFinal = self.samplingInput
        else:
            self.inputMics = self.inputVolumes.get()
            self.samplingOriginal = self.inputMics.getSamplingRate()
            if self.downsampleType.get() == ORIGINAL:
                # If 'original' get sampling rate from original micrographs
                self.samplingFinal = self.samplingOriginal
            else:
                # IF 'other' multiply the original sampling rate by the factor provided
                self.samplingFinal = self.samplingOriginal*self.downFactor.get()
        
    
    def getInputMicrographs(self):
        """ Return the micrographs associated to the SetOfCoordinates or to the 
        Selected micrographs if Same as Picking not chosen. """
        if self.downsampleType == SAME_AS_PICKING:
            return self.inputCoordinates.get().getMicrographs()
        else:
            return self.inputMicrographs.get()
    
    def getImgIdFromCoord(self, coordId):
        """ Get the image id from the related coordinate id. """
        '%s:%06d'
        parts = coordId.split(':')
        imgFn = self._getExtraPath(replaceBaseExt(parts[0], "stk")) 
        
        return '%06d@%s' %(int(parts[1]), imgFn)
    
    def _storeMethodsInfo(self, fnVolumes):
        """ Store some information when the protocol finishes. """
        mdVols = md.MetaData(fnVolumes)
        total = mdVols.size() 
        mdVols.removeDisabled()
        zScoreMax = mdVols.getValue(md.MDL_ZSCORE, mdVols.lastObject())
        numEnabled = mdVols.size()
        numRejected = total - numEnabled

        msg = ""

        if self.doSort:
            if self.rejectionMethod != REJECT_NONE:
                msg = " %d of them were rejected with Zscore greater than %.2f." % (numRejected, zScoreMax)

        self.methodsVar.set(msg)

    def getCoords(self):
        if self.inputCoordinates.hasValue():
            return self.inputCoordinates.get()
        else:
            return None

    def getOutput(self):
        if (self.hasAttribute('outputParticles') and
            self.outputParticles.hasValue()):
            return self.outputParticles
        else:
            return None

    def getBoxSize(self):
        # This function is needed by the wizard
        # Get input coordinates from protocol and if they have not value leave the existing boxSize value
        inputCoords = self.getCoords()
        if  inputCoords is None:
            return self.boxSize.get()

        # Get boxSize from coordinates and sampling input from associated micrographs
        boxSize = inputCoords.getBoxSize()
        samplingInput = inputCoords.getMicrographs().getSamplingRate()

        # If downsampling type same as picking sampling does not change
        if self.downsampleType.get() == SAME_AS_PICKING:
            samplingFinal = samplingInput
        else:
            if self.getInputMicrographs() is not None:
                samplingMics = self.getInputMicrographs().getSamplingRate()
            else:
                return self.boxSize.get()

            if self.downsampleType.get() == ORIGINAL:
                # If 'original' get sampling rate from original micrographs
                samplingFinal = samplingMics
            else:
                # IF 'other' multiply the original sampling rate by the factor provided
                samplingFinal = samplingMics*self.downFactor.get()

        downFactor = samplingFinal/samplingInput

        return int(boxSize/downFactor)
    
    def _getOutputVolMd(self):
        return self._getPath('volumes.xmd')
    