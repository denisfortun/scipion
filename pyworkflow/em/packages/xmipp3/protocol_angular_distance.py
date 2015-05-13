# **************************************************************************
# *
# * Authors:     Roberto Marabini (roberto@cnb.csic.es)
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
This sub-package contains wrapper around angular_break_symmetry Xmipp program
"""

#from pyworkflow.object import String
from pyworkflow.em.protocol import ProtProcessParticles
from convert import writeSetOfParticles, readSetOfParticles
from pyworkflow.protocol.params import (PointerParam, StringParam, LEVEL_ADVANCED)



        
        
class XmippProtAngDist(ProtProcessParticles):
    """ angular distance between two sets of particles """
    _label = 'angular distance'

    #--------------------------- DEFINE param functions --------------------------------------------
    def _defineParams(self, form):

        form.addSection(label='Input')
        form.addParam('inputParticles', PointerParam,
                      pointerClass='SetOfParticles',
                      label="Angles information 1",pointerCondition='hasAlignment',
                      help='Select the input particles-1. ')

        form.addParam('inputParticles2', PointerParam,
                      pointerClass='SetOfParticles',
                      label="Angles information 2",pointerCondition='hasAlignment',
                      help='Select the input particles-2. ')


        form.addParam('symmetryGroup', StringParam, default="c1",
                      label='Symmetry group',
                      help="See http://xmipp.cnb.csic.es/twiki/bin/view/Xmipp/Symmetry"
                           " for a description of the symmetry groups format in Xmipp.\n"
                           "If no symmetry is present, use _c1_.")

        form.addParam('extraParams', StringParam, default='',
                      expertLevel=LEVEL_ADVANCED,
                      label='Additional parameters',
                      help='')


    def _getDefaultParallel(self):
        """This protocol doesn't have mpi version"""
        return (0, 0)

    #--------------------------- INSERT steps functions --------------------------------------------
    def _insertAllSteps(self):
        """ Mainly prepare the command line for call brak symmetry program"""
        # Create a metadata with the geometrical information
        # as expected by Xmipp
        #--------------------------- STEPS functions --------------------------------------------
        self.outImagesMd = self._getPath('out')
        imgsFn1 = self._getPath('input_particles1.xmd')
        imgsFn2 = self._getPath('input_particles2.xmd')
        self._insertFunctionStep('convertInputStep', imgsFn1, imgsFn2)
        self._insertFunctionStep('computeAngDistStep', imgsFn1, imgsFn2)
        #self._insertFunctionStep('createOutputStep')

    #--------------------------- STEPS functions --------------------------------------------

    def convertInputStep(self, outputFn1, outputFn2):
        """ Create a metadata with the images and geometrical information. """
        writeSetOfParticles(self.inputParticles.get(), outputFn1)
        writeSetOfParticles(self.inputParticles2.get(), outputFn2)

    def computeAngDistStep(self, imgsFn1, imgsFn2):
        args = "--ang1 Particles@%s --ang2 Particles@%s  --sym %s --oroot %s" % \
               (imgsFn1, imgsFn2, self.symmetryGroup.get(), self.outImagesMd )
        self.runJob("xmipp_angular_distance ", args)
        #self.outputMd = String(outImagesMd+'.xmd')

    #def createOutputStep(self):
    #    imgSet = self._createSetOfParticles()
    #    imgSet.copyInfo(self.inputParticles.get())
    #    readSetOfParticles(self.outputMd.get(), imgSet)

    #    self._defineOutputs(outputParticles=imgSet)

    #--------------------------- INFO functions --------------------------------------------                
    def _summary(self):
        import os
        summary = []
        if not hasattr(self, 'outputParticles'):
            summary.append("Output particles not ready yet.")
        else:
            summary.append("Symmetry: %s"% self.symmetryGroup.get())
        return summary

    def _validate(self):
        pass

    def _citations(self):
        return []

    def _methods(self):
        methods = []
        return methods
    
