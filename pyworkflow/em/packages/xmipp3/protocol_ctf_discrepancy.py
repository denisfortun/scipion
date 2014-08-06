# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *              Roberto Marabini (roberto@cnb.csic.es)
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
This sub-package contains the XmippCtfMicrographs protocol
"""

from pyworkflow.em import *  
from pyworkflow.utils.path import makePath, moveFile, removeBaseExt
from convert import *
from xmipp3 import XmippMdRow
from pyworkflow.protocol.constants import LEVEL_EXPERT, STEPS_PARALLEL
import xmipp
import collections


class XmippProtCTFDiscrepancy(ProtCTFMicrographs):
    """Protocol to estimate CTF on a set of micrographs using xmipp3"""
    _label = 'ctf discrepancy'
    
    def __init__(self, **args):
        ProtCTFMicrographs.__init__(self, **args)
        #uncomment if you do not inherit from ProtCTFMicrographs
        #self.methodsInfo = String()
        #self.stepsExecutionMode = STEPS_PARALLEL
        self._freqResol = {}

    def _defineParams(self, form):
        form.addSection(label='Input')
        # Read N ctfs estimations
        form.addParam('inputCTFs', MultiPointerParam, label="input CTFs",
                      pointerClass='SetOfCTF',
                      help='Select the first set of CTFs to compare')        

        form.addParallelSection(threads=4, mpi=0)       
#--------------------------- INSERT steps functions --------------------------------------------  
    def _iterMethods(self):
        for method1 in self.methodNames:
            for method2 in self.methodNames:
                if method1 < method2:
                    for ctf in self.setOfCTF:
                        yield method1, method2, ctf
                                
    def _insertAllSteps(self):
        """for each ctf insert the steps to compare it
        """
        self.setOfCTF = self.inputCTFs[0].get()
        #self.setOfCTF2 = self.inputCTFs[1].get()
        self.methodNames = collections.OrderedDict()
        for i, ctf in enumerate(self.inputCTFs):
            protocol = self.getMapper().getParent(ctf.get())
            self.methodNames[i] = "(%d) %s " % (i+1, protocol.getClassLabel())

        
        deps = [] # Store all steps ids, final step createOutput depends on all of them
        # For each ctf pair insert the steps to process it
        # check same size, same micrographs
        for method1, method2, ctf in self._iterMethods():
            stepId = self._insertFunctionStep('_computeCTFDiscrepancyStep' 
                                              , ctf.getObjId()
                                              , method1
                                              , method2
                                              ,prerequisites=[]) # Make estimation steps independent
                                                                 # between them
            deps.append(stepId)
        # Insert step to create output objects       
        self._insertFunctionStep('createOutputStep', prerequisites=deps)
    
    def _computeCTFDiscrepancyStep(self, ctfId, method1, method2):
        #TODO must be same micrographs
        #convert to md
        mdList = [xmipp.MetaData(), xmipp.MetaData()]
        ctfList = [self.inputCTFs[method1].get()[ctfId], self.inputCTFs[method2].get()[ctfId]]
        ctfRow = XmippMdRow()
        
        for md, ctf in izip(mdList, ctfList):
            objId = md.addObject()
            ctfModelToRow(ctf, ctfRow)
            micrographToRow(ctf.getMicrograph(), ctfRow)
            ctfRow.writeToMd(md, objId)
        self._freqResol[(method1, method2, ctfId)] = xmipp.errorMaxFreqCTFs2D(*mdList)

    def createOutputStep(self):
        ctfSet = self._createSetOfCTF()
#        ctfSet.setMicrographs(self.setOfCTF.getMicrographs())
        #import pdb
        #pdb.set_trace()
        for method1, method2, ctfId in self._freqResol:
            ctf = CTFModel()
            ctf1 = self.inputCTFs[method1].get()[ctfId]
            ctf2 = self.inputCTFs[method2].get()[ctfId]
            ctf.setDefocusU( (ctf1.getDefocusU() + ctf2.getDefocusU())/2. )
            ctf.setDefocusV( (ctf1.getDefocusV() + ctf2.getDefocusV())/2. )
            ctf.setDefocusAngle( (ctf1.getDefocusAngle() + ctf2.getDefocusAngle())/2. )
            ctf.setMicrograph(ctf1.getMicrograph())
            #SAme ctf apear many times so I can not keep the ctfId
            #ctf.setObjId(ctfId)
            ctf.resolution = Float(self._freqResol[(method1, method2, ctfId)])
            ctf.method1 = String(self.methodNames[method1])
            ctf.method2 = String(self.methodNames[method2])
            # save the values of defocus for each micrograph in a list
            ctfSet.append(ctf)
            ctf.cleanObjId()
        self._defineOutputs(outputCTF=ctfSet)
        
    def _citations(self):
        return ['Marabini2014a']
    
    def _summary(self):
        message = []
        for i, ctf in enumerate(self.inputCTFs):
            protocol = self.getMapper().getParent(ctf.get())
            message.append("Method %d %s" % (i+1, protocol.getClassLabel()))
        #TODO size de la cosa calculada
        ####message.append("Comparered <%d> micrograph" % (size,'micrographs'))
        return message    
    
    def _methods(self):
        pass#nothing here
    
    def _validate(self):
        """ The function of this hook is to add some validation before the protocol
        is launched to be executed. It should return a list of errors. If the list is
        empty the protocol can be executed.
        """
        #same micrographs in both CTF??
        errors = [ ] 
        # Add some errors if input is not valid
        return errors
