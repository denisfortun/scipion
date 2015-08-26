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
                      pointerClass='Volume',# pointerCondition='hasRepresentatives',
                      help='Select the input fluorescence volume from the project.')  
        form.addParam('inputPSF', PointerParam, label="PSF", important=True,
                      pointerClass='Volume',
                      help='Select the PSF ')
        
        form.addParallelSection(threads=4, mpi=1)

    #--------------------------- INSERT steps functions --------------------------------------------  
    def _insertAllSteps(self):
#         self._insertFunctionStep('convolve')

        self._insertFunctionStep('createOutputStep')
    
    #--------------------------- STEPS functions --------------------------------------------
    def createOutputStep(self):
        # Temporary solution specific to my machine
        # Command lines options of matlab don't work if I don't use directly the binary file in the Matlab folder
        fnMatlab = "/home/big/public_bin/MATLAB/R2011a/bin/glnxa64/MATLAB"
        
        fluoVol = self.inputFluo3D.get()
        fnFluoVol = fluoVol.getFileName()
        psf = self.inputPSF.get()
        fnPsf = psf.getFileName()
        fnRoot = self._getExtraPath(pwutils.removeBaseExt(fnFluoVol))
        # Get the absolute path here
        fnProject = "/home/big/ScipionUserData/projects/Fluorescence_3D_2/"

        from pyworkflow.em.packages.xmipp3 import getMatlabEnviron
#        args='''-nodesktop -r "diary('%s'); bigfluo_convolution3D('%s','%s','%s'); exit"'''%(fnProject+fnRoot+"_matlab.log",fnProject+fnFluoVol,fnProject+fnPsf,fnProject+fnRoot)
#        args=''' -nodesktop -r "cd /home/big/Documents/Denis/scipion/matlab_code/test; test_convolution3D; exit"'''
        args=''' -nodesktop ;exit"'''
        print(args)
        print("########  launch matlab") 
        self.runJob("%s " % fnMatlab, args, env=getMatlabEnviron())
        print("########  exit matlab") 
        #/home/big/public_bin/MATLAB/R2011a/bin/glnxa64/MATLAB -nodesktop -r "cd /home/big/Documents/Denis/scipion/matlab_code/test; test_convolution3D;exit"

        dimx = fluoVol.getDim()[0]
        dimy = fluoVol.getDim()[1]
        dimz = fluoVol.getDim()[2]
        
        #self.runJob("xmipp_image_convert", "-i %s_convolved.raw#%d,%d,%d,0,float -o %s_convolved.vol" % (fnRoot,dimx,dimy,dimz,fnRoot),env=xmipp3.getEnviron())
        fnOut = "%s_convolved.vol" % fnRoot
        ih = ImageHandler()
        ih.convert("%s_convolved.raw#%d,%d,%d,0,float" % (fnRoot,dimx,dimy,dimz,), fnOut)
        
        outputFluoVol = Volume()
        outputFluoVol.setFileName(fnOut)
        
        self._defineOutputs(outputFluo3D=outFluoVol)

