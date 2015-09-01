# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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
This sub-package contains a protocol for applying 3D alignment parameters to a set of volumes
"""

from pyworkflow.em import *
from pyworkflow.em.packages.xmipp3.utils import iterMdRows
from pyworkflow.em.packages.xmipp3.convert import (xmippToLocation, writeSetOfVolumes)
from pyworkflow.em.convert import ImageHandler
from protocol_align_3D import ProtAlign3D

import xmipp

       
        
class ProtApplyAlignment3D(ProtAlign3D):
    """ Apply alignment parameters and produce a new set of volumes. """
    _label = 'apply 3D alignment'

    #--------------------------- DEFINE param functions --------------------------------------------
    
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('inputVolumes', PointerParam, important=True,
                      label="input volumes", pointerClass='SetOfVolumes')
        # Hook that should be implemented in subclasses

    #--------------------------- INSERT steps functions --------------------------------------------
    
    def _insertAllSteps(self):
        """ Mainly prepare the command line for call cl2d align program"""
        
        # Create a metadata with the geometrical information 
        # as expected by Xmipp
        imgsFn = self._getPath('input_volumes.xmd')
        self._insertFunctionStep('convertInputStep', imgsFn)
        self._insertFunctionStep('applyAlignmentStep', imgsFn)
        self._insertFunctionStep('createOutputStep')        

    #--------------------------- STEPS functions --------------------------------------------        
    
    def convertInputStep(self, outputFn):
        """ Create a metadata with the images and geometrical information. """
        writeSetOfVolumes(self.inputVolumes.get(), outputFn)
        
        return [outputFn]
    
    def applyAlignmentStep(self, inputFn):
        """ Create a metadata with the volumes and geometrical information. """
        outputStk = self._getPath('aligned_volumes.stk')
        args = '-i %(inputFn)s -o %(outputStk)s --apply_transform ' % locals()
        self.runJob('xmipp_transform_geometry', args)
        
        return [outputStk]

    def _updateItem(self, item, row):
        """ Implement this function to do some
        update actions over each single item
        that will be stored in the output Set.
        """
        # By default update the item location (index, filename) with the new binary data location
        newFn = row.getValue(xmipp.MDL_IMAGE)
        newLoc = xmippToLocation(newFn)
        item.setLocation(newLoc)
        # Also remove alignment info
        item.setTransform(None)

            
    def createOutputStep(self):
        particles = self.inputVolumes.get()

        # Generate the SetOfAlignmet
        alignedSet = self._createSetOfVolumes()
        alignedSet.copyInfo(volumes)

        inputMd = self._getPath('aligned_volumes.xmd')
        alignedSet.copyItems(volumes,
                             updateItemCallback=self._updateItem,
                             itemDataIterator=iterMdRows(inputMd))
        # Remove alignment 2D
        alignedSet.setAlignment(ALIGN_NONE)

        # Define the output average

        avgFile = self._getExtraPath("average.xmp")

        imgh = ImageHandler()
        avgImage = imgh.computeAverage(alignedSet)

        avgImage.write(avgFile)

        avg = Particle()
        avg.setLocation(1, avgFile)
        avg.copyInfo(alignedSet)

        self._defineOutputs(outputAverage=avg)
        self._defineSourceRelation(self.inputVolumes, avg)

        self._defineOutputs(outputVolumes=alignedSet)
        self._defineSourceRelation(self.inputVolumes, alignedSet)
                

    #--------------------------- INFO functions --------------------------------------------
    def _validate(self):
        errors = []
        if not self.inputVolumes.get().hasAlignment3D():
            errors.append("Input particles should have alignment 3D.")
        return errors
        
    def _summary(self):
        summary = []
        if not hasattr(self, 'outputVolumes'):
            summary.append("Output volumes not ready yet.")
        else:
            summary.append("Applied alignment to %s volumes." % self.inputVolumes.get().getSize())
        return summary

    def _methods(self):
        if not hasattr(self, 'outputVolumes'):
            return ["Output volumes not ready yet."]
        else:
            return ["We applied alignment to %s volumes from %s and produced %s."
                    % (self.inputVolumes.get().getSize(), self.getObjectTag('inputVolumes'), self.getObjectTag('outputVolumes'))]

    
