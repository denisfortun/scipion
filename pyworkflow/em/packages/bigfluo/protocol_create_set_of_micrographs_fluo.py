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
This sub-package contains protocols for creating 3D masks.
"""

import pyworkflow.utils as pwutils
from pyworkflow.em import *  

AVERAGE = 0

class ProtCreateSetMicFluo(EMProtocol):
    """ Create a Set of set 2D micrographs from a set of 3D fluorescence volumes.
    """
    _label = 'create set of micrographs'
    
    #--------------------------- DEFINE param functions --------------------------------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('inputSetOfFluo3D', PointerParam, pointerClass="SetOfFluo3D", 
                      label="Input fluorescence volumes",
                      help="Select the volume that will be preprocessed for manual picking")

        form.addParam('method', EnumParam, default=AVERAGE,
              choices=['Average'],
              label='Method')

    #--------------------------- INSERT steps functions --------------------------------------------
    def _insertAllSteps(self):
        #if self.method == AVERAGE:
        #    self._insertFunctionStep('createSlicesAverage')

        self._insertFunctionStep('createOutputStep')
    
    #--------------------------- STEPS functions --------------------------------------------

    def createOutputStep(self):
        volumes = self.inputSetOfFluo3D.get()
        outSetOfMic = self._createSetOfMicrographs() 
        outSetOfMic.setSamplingRate(1.0)  
        mic = Micrograph()
        ih = ImageHandler()
        
        for fluo3D in volumes:
            fnVol = fluo3D.getFileName()
            avgFn = self._getExtraPath(pwutils.removeBaseExt(fnVol)) 
            self.createAverage(fnVol, avgFn)  
            ih.convert(avgFn + "_average.xmp", avgFn + "_average.tif")
            mic.setFileName(avgFn + "_average.tif")
            mic.copyObjId(fluo3D)
            outSetOfMic.append(mic)       
        
        self._defineOutputs(outputMask=outSetOfMic)
        
    def createAverage(self, fnVol, avgFn):
        """ Compute the average "micrograph" from a given fluo3D file. """
        import pyworkflow.em.packages.xmipp3 as xmipp3
        self.runJob("xmipp_image_statistics", "-i %s -v 0 --save_image_stats %s_" % (fnVol, avgFn), 
                    env=xmipp3.getEnviron())          
