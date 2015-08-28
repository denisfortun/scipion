# **************************************************************************
# *
# * Authors:     Denis Fortun (denis.fortun@epfl.ch)
# *              Carlos Oscar S. Sorzano (coss@cnb.csic.es)
#                J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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
This sub-package contains protocols for applying classification and alignement parameters to a set of particles.
"""

import pyworkflow.utils as pwutils
from pyworkflow.em import *  
from pyworkflow.em.protocol import SetOfClasses2D


class ProtApplyClassAlign2D(EMProtocol):
    """ Apply classification and alignement parameters to a set of particles.
    """
    _label = 'apply classif parameters'
    
    #--------------------------- DEFINE param functions --------------------------------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('inputSetOfClasses2D', PointerParam, pointerClass="SetOfClasses2D", 
                      label="Input 2D classes",
                      help="Select the set of classes to use")

        form.addParam('inputSetOfParticles', PointerParam, pointerClass="SetOfParticles", 
                      label="Input particles",
                      help="Select the set of particles to classify")

    #--------------------------- INSERT steps functions --------------------------------------------
    def _insertAllSteps(self):
        #if self.method == AVERAGE:
        #    self._insertFunctionStep('createSlicesAverage')
        Particle
        self._insertFunctionStep('createOutputStep')
    
    #--------------------------- STEPS functions --------------------------------------------

    def _updateParticle(self, origParticle, classParticle):
        origParticle.setClassId(classParticle.getClassId())
        origParticle.setTransform(classParticle.getTransform())
        
    def _updateClass(self, newClass):
        newClass.setAlignment2D()
        
        
    def createOutputStep(self):
        # Create a temporary set of particles to be iterated
        # sorted by id and in the same order of input particles
        # since by default they grouped by classes
        classifiedParts = SetOfParticles(filename=":memory:")
        classifiedParts.appendFromClasses(self.inputSetOfClasses2D.get())
        
        outputClasses = self._createSetOfClasses2D(self.inputSetOfParticles.get())
                
        outputClasses.classifyItems(updateItemCallback=self._updateParticle,
                                    updateClassCallback=self._updateClass,
                                    itemDataIterator=iter(classifiedParts))
        
        self._defineOutputs(outputClasses=outputClasses)

