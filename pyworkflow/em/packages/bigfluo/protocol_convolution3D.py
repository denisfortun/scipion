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
from pyworkflow.em.packages.bigfluo.data import Fluo3D
"""
This sub-package contains the ProtConvolution3D protocol
"""

import pyworkflow.utils as pwutils
from pyworkflow.em import *  

                
class ProtConvolution3D(EMProtocol):
    """Protocol to apply 3D convolution to a Fluo3D object """
    _label = 'Apply 3D convolution'
    
    #--------------------------- DEFINE param functions --------------------------------------------   
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('inputFluo3D', PointerParam, label="Input volume", important=True, 
                      pointerClass='Fluo3D',# pointerCondition='hasRepresentatives',
                      help='Select the input fluorescence volume from the project.')  
        form.addParam('inputPSF', PointerParam, label="PSF", important=True,
                      pointerClass='Volume',
                      help='Select the PSF ')
        
        form.addParallelSection(threads=4, mpi=1)

    #--------------------------- INSERT steps functions --------------------------------------------  
    def _insertAllSteps(self):
        self._insertFunctionStep('convolve')

        self._insertFunctionStep('createOutputStep')
    
    #--------------------------- STEPS functions --------------------------------------------
    def convolve(self):
        fluoVol = self.inputFluo3D.get()
        fnFluoVol = fluoVol.getFileName()
        psf = self.inputPSF.get()
        fnPsf = psf.getFileName()
        fnOut = self._getExtraPath(pwutils.removeBaseExt(fnFluoVol) + "_conv.vol")
        
        args='''-r "diary('%s'); convolution3D('%s','%s','%s','%s'); exit"'''%(fnRoot+"_matlab.log",fnFluoVol,fnPsf,fnOut)
        self.runJob("matlab", args, env=getMatlabEnviron(mirtDir))

    def createOutputStep(self, fnOut):
        outFluoVol = Fluo3D(fnOut)
        
        self._defineOutputs(outputFluo3D=outFluoVol)
        