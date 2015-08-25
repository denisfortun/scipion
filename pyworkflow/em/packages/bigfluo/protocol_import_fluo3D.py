# **************************************************************************
# *
# * Authors:     Denis Fortun (denis.fortun@epfl.ch)
# *              J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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
This sub-package contains the XmippParticlePicking protocol
"""
import os

import pyworkflow.em as em
import pyworkflow.protocol.params as params
from pyworkflow.utils.properties import Message

from data import Fluo3D, SetOfFluo3D


class ProtImportFluo3D(em.ProtImportImages):
    """Protocol to import a set of volumes to the project"""
    _label = 'import fluo3D'
    
    def __init__(self, **args):
        em.ProtImportImages.__init__(self, **args)         
       
    def _defineAcquisitionParams(self, form):
        """ Define acquisition parameters, it can be overriden
        by subclasses to change what parameters to include.
        """
        form.addParam('samplingRate', params.FloatParam,
                   label=Message.LABEL_SAMP_RATE)
    
    def _insertAllSteps(self):
        self._insertFunctionStep('importVolumesStep', self.getPattern(), self.samplingRate.get())

    #--------------------------- STEPS functions ---------------------------------------------------
    
    def importVolumesStep(self, pattern, samplingRate):
        """ Copy images matching the filename pattern
        Register other parameters.
        """
        self.info("Using pattern: '%s'" % pattern)

        # Create a Volume template object
        vol = em.Volume()#Fluo3D()
        vol.setSamplingRate(self.samplingRate.get())
        copyOrLink = self.getCopyOrLink()
        imgh = em.ImageHandler()

        #volSet = self._createSetOfFluo3D()
        volSet = self._createSetOfVolumes()
        volSet.setSamplingRate(self.samplingRate.get())

        for fileName, fileId in self.iterFiles():
            dst = self._getExtraPath(os.path.basename(fileName))
            copyOrLink(fileName, dst)
            x, y, z, n = imgh.getDimensions(dst)
            # First case considers when reading mrc without volume flag
            # Second one considers single volumes (not in stack)
            if (z == 1 and n != 1) or (z !=1 and n == 1):
                vol.setObjId(fileId)
                if dst.endswith('.mrc'):
                    dst += ':mrc'
                vol.setLocation(dst)
                volSet.append(vol)
            else:
                for index in range(1, n+1):
                    vol.cleanObjId()
                    vol.setLocation(index, dst)
                    volSet.append(vol)

        if volSet.getSize() > 1:
            self._defineOutputs(outputVolumes=volSet)
        else:
            self._defineOutputs(outputVolume=vol)

    #--------------------------- INFO functions ----------------------------------------------------
    
    def _getVolMessage(self):
        if self.hasAttribute('outputVolume'):
            return "Volume %s"% self.getObjectTag('outputVolume')
        else:
            return "Volumes %s" % self.getObjectTag('outputVolumes')
        
    def _summary(self):
        summary = []
        if self.hasAttribute('outputVolume') or self.hasAttribute('outputVolumes'):
            summary.append("%s imported from:\n%s" % (self._getVolMessage(), self.getPattern()))

            summary.append("Sampling rate: *%0.2f* (A/px)" % self.samplingRate.get())
        return summary
    
    def _methods(self):
        methods = []
        if self.hasAttribute('outputVolume') or self.hasAttribute('outputVolumes'):
            methods.append(" %s imported with a sampling rate *%0.2f*" % (self._getVolMessage(), self.samplingRate.get()),)
        return methods

    #--------------------------- UTILS functions ----------------------------------------------------    
    def _createSetOfFluo3D(self, suffix=''):
        return self._createSet(SetOfFluo3D, 'fluo3Ds%s.sqlite', suffix)
    
    





