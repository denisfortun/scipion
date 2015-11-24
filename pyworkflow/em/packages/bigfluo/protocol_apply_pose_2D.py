# # **************************************************************************
# # *
# # * Authors:     Denis Fortun (denis.fortun@epfl.ch)
# # *
# # * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# # *
# # * This program is free software; you can redistribute it and/or modify
# # * it under the terms of the GNU General Public License as published by
# # * the Free Software Foundation; either version 2 of the License, or
# # * (at your option) any later version.
# # *
# # * This program is distributed in the hope that it will be useful,
# # * but WITHOUT ANY WARRANTY; without even the implied warranty of
# # * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # * GNU General Public License for more details.
# # *
# # * You should have received a copy of the GNU General Public License
# # * along with this program; if not, write to the Free Software
# # * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# # * 02111-1307  USA
# # *
# # *  All comments concerning this program package may be sent to the
# # *  e-mail address 'jmdelarosa@cnb.csic.es'
# # *
# # **************************************************************************
# """
# This sub-package contains protocols for applying angle and shift  parameters obtained with projection matching to a set of 2D particles.
# """
# 
# import pyworkflow.utils as pwutils
# from pyworkflow.em import *  
# from pyworkflow.em.protocol import SetOfParticles
# 
# 
# class ProtApplyPose2D(EMProtocol):
#     """ Apply angle and shift  parameters obtained with projection matching to a set of 2D particles.
#     """
#     _label = 'apply angle and shift  parameters obtained with projection matching'
#     
#     #--------------------------- DEFINE param functions --------------------------------------------
#     def _defineParams(self, form):
#         form.addSection(label='Input')
#         
#         form.addParam('InputSetOfParticles', PointerParam, pointerClass="SetOfParticles", 
#                       label="Input Particles 2",
#                       help="Select the input set of particles")
# 
#         form.addParam('SetOfParticlesWithPoses', PointerParam, pointerClass="SetOfParticles", 
#                       label="Particles with pose parameters",
#                       help="Select the set of particles with pose parameters")
# 
#     #--------------------------- INSERT steps functions --------------------------------------------
#     def _insertAllSteps(self):
#         #if self.method == AVERAGE:
#         #    self._insertFunctionStep('createSlicesAverage')
#         self._insertFunctionStep('createOutputStep')
#     
#     #--------------------------- STEPS functions --------------------------------------------
# 
#     def _updateParticle(self, origParticle, classParticle):
# #         origParticle.setClassId(classParticle.getClassId())
#         origParticle.setTransform(classParticle.getTransform())
# 
# #     def _updateClass(self, newClass):
# #         newClass.setAlignment3D()
# #         oldClass = self.inputSetOfClasses3D.get()[newClass.getObjId()]
# #         newClass.setRepresentative(oldClass.getRepresentative())
#         
#         
#     def createOutputStep(self):
#         # Create a temporary set of particles to be iterated
#         # sorted by id and in the same order of input particles
#         # since by default they grouped by classes
#         classifiedParts = SetOfParticles(filename=":memory:")
#         classifiedParts.appendFromImages(self.SetOfParticlesWithPoses.get())
#         
# #         outputClasses = self._createSetOfParticles(self.InputSetOfParticles.get())
# #                 
# #         outputClasses.classifyItems(updateItemCallback=self._updateParticle,
# # #                                     updateClassCallback=self._updateClass,
# #                                     itemDataIterator=iter(classifiedParts))
#         
#         self._defineOutputs(outputParticles=classifiedParts)
from pyworkflow.em.packages.xmipp3.convert import alignmentToRow, imageToRow

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
This sub-package contains protocols for applying classification and alignement parameters to a set of 3D particles.
"""

import pyworkflow.utils as pwutils
from pyworkflow.em import *  
from pyworkflow.em.protocol import SetOfParticles
from pyworkflow.em.packages.xmipp3.xmipp3 import *
from pyworkflow.em.packages.xmipp3 import writeSetOfParticles, readSetOfParticles

class ProtApplyPose2D(EMProtocol):
    """ Apply classification and alignement parameters to a set of 3D particles.
    """
    _label = 'apply 3D classif parameters'
    
    #--------------------------- DEFINE param functions --------------------------------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('InputSetOfParticles', PointerParam, pointerClass="SetOfParticles", 
                      label="Input Particles 2",
                      help="Select the input set of particles")
 
        form.addParam('SetOfParticlesWithPoses', PointerParam, pointerClass="SetOfParticles", 
                      label="Particles with pose parameters",
                      help="Select the set of particles with pose parameters")

    #--------------------------- INSERT steps functions --------------------------------------------
    def _insertAllSteps(self):
        self._insertFunctionStep('convertInputStep')
        self._insertFunctionStep('createOutputStep')
    
    #--------------------------- STEPS functions --------------------------------------------

    def convertInputStep(self):
        """ Generated the input particles metadata expected 
        by projection matching. And copy the generated file to be
        used as initial docfile for further iterations.
        """
        writeSetOfParticles(self.InputSetOfParticles.get(), self._getExtraPath('inputParticules.xmd'))

    def _updateItem(self, newPart, origPart):
        newPart.setTransform(origPart.getTransform())
         
    def _applyMetadata(self,inputSetOfParticles, otherSet, outputSetOfParticles):
        itemDataIterator=iter(otherSet)
         
        for item in inputSetOfParticles:
            newItem = item.clone()
            row = None if itemDataIterator is None else next(itemDataIterator)
            self._updateItem(newItem, row)
            outputSetOfParticles.append(newItem)

    def createOutputStep(self):
        partsPose = self.SetOfParticlesWithPoses.get()
        inputParts = self.InputSetOfParticles.get()
        outputParts = self._createSetOfParticles()
        
        self._applyMetadata(inputParts, partsPose, outputParts)
        writeSetOfParticles(outputParts, self._getPath('outputParticles.xmd'))
        
        # Write pose parameters in row form
#         fnOutputParts = self._getPath('outputParticulesRow.xmd')
#         MD = MetaData(self._getExtraPath('inputParticules.xmd'))
#         row = XmippMdRow()
#         for part in partsPose:
#             # Assumption: corresponding particles in the two sets have the same id
#             id = part.getObjId()
#     
#             alignmentToRow(part.getTransform(), row, ALIGN_3D)
#             rot =  row.getValue(xmipp.MDL_ANGLE_ROT,id)
#             tilt = row.getValue(xmipp.MDL_ANGLE_TILT,id)
#             psi = row.getValue(xmipp.MDL_ANGLE_PSI,id)
#             x = row.getValue(xmipp.MDL_SHIFT_X,id)
#             y = row.getValue(xmipp.MDL_SHIFT_Y,id)
#              
#             MD.setValue(xmipp.MDL_ANGLE_ROT, rot, id)
#             MD.setValue(xmipp.MDL_ANGLE_TILT, tilt, id)
#             MD.setValue(xmipp.MDL_ANGLE_PSI, psi, id)
#             MD.setValue(xmipp.MDL_SHIFT_X, x,id)
#             MD.setValue(xmipp.MDL_SHIFT_Y, y,id)
#         MD.write(fnOutputParts)
#          
#         outputParts = self._createSetOfParticles()
#         readSetOfParticles(fnOutputParts, outputParts)
        self._defineOutputs(outputParticles=outputParts)

