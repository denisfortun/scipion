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
from pyworkflow.em.packages.bigfluo.data import Fluo3D,SetOfFluo3D

"""
This sub-package contains the ProtConvolution3D protocol
"""

import pyworkflow.utils as pwutils
from pyworkflow.em import *  
          
class ProtConvMatch(EMProtocol):
    """Protocol to compute the average of a set of Fluo3D """
    _label = 'convolution matching'
    
    #--------------------------- DEFINE param functions --------------------------------------------   
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('inputSetOfFluo3D', PointerParam, label="Input volumes", important=True, 
                      pointerClass='SetOfVolumes',# pointerCondition='hasRepresentatives',
                      help='Select the input set of fluorescence volumes.')  

        form.addParam('initVolume', PointerParam, label="Initial volume", important=True, 
                      pointerClass='Volume',# pointerCondition='hasRepresentatives',
                      help='Select the initial volume.')  

        form.addParam('psf', PointerParam, label="psf", important=True, 
                      pointerClass='Volume',# pointerCondition='hasRepresentatives',
                      help='Select the PSF.')  
        
    #--------------------------- INSERT steps functions --------------------------------------------  
    def _insertAllSteps(self):
#         self._insertFunctionStep('convolve')

        self._insertFunctionStep('createOutputStep')
    
    #--------------------------- STEPS functions --------------------------------------------
    def createOutputStep(self):
        setOfFluoVols = self.inputSetOfFluo3D.get()
        fnSetOfFluoVols_stk = list(setOfFluoVols.getFiles())[0]
        initVol = self.initVolume.get()
        fnInitVol = initVol.getFileName()
        psf = self.psf.get()
        fnPsf= psf.getFileName()
        print("###########################################################")
        print(fnInitVol)
        print(fnPsf)
        fnRoot = self._getExtraPath(pwutils.removeBaseExt(fnSetOfFluoVols_stk))
    
        from pyworkflow.em.packages.xmipp3 import getMatlabEnviron
        args=''' -r "diary('%s'); bigfluo_convolution_matching('%s','%s','%s','%s'); exit"'''%(fnRoot+"_matlab.log",fnSetOfFluoVols_stk,fnPsf,fnInitVol,fnRoot)
        self.runJob("matlab", args, env=getMatlabEnviron())
 
        dimx = setOfFluoVols.getDim()[0]
        dimy = setOfFluoVols.getDim()[1]
        dimz = setOfFluoVols.getDim()[2]
         
        fnOut = "%s_outVol.vol" % fnRoot
        ih = ImageHandler()
        ih.convert("%s_average.raw#%d,%d,%d,0,float" % (fnRoot,dimx,dimy,dimz), fnOut)
         
        outputFluoVol = Fluo3D()
        outputFluoVol.setFileName(fnOut)
         
        self._defineOutputs(outputFluo3D=outputFluoVol)
