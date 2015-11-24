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
This sub-package contains the ProtSimuFluoParticles protocol
"""

import pyworkflow.utils as pwutils
from pyworkflow.em import *  

                
class ProtSimuFluoParticles3D(EMProtocol):
    """Protocol to compute the average of a set of Fluo3D """
    _label = 'Simulation of 3D fluorescence data'
    
    #--------------------------- DEFINE param functions --------------------------------------------   
    def _defineParams(self, form):
        form.addSection(label='Input')
        
        form.addParam('inputVolume', PointerParam, label="Input particle", important=True, 
                      pointerClass='Volume',# pointerCondition='hasRepresentatives',
                      help='Select the input particle to simulate fluorescence data.')  
        form.addParam('inputPSF', PointerParam, label="PSF", important=True,
                      pointerClass='Volume',
                      help='Select the PSF ')
        form.addParam('posesFile', StringParam,
              label='List of poses',  
              help="File containing the list of angles and shifts.")

    #--------------------------- INSERT steps functions --------------------------------------------  
    def _insertAllSteps(self):
#         self._insertFunctionStep('convolve')

        self._insertFunctionStep('createOutputStep')
    
    #--------------------------- STEPS functions --------------------------------------------
    def createOutputStep(self):
        inVol = self.inputVolume.get()
        fnInVol = inVol.getFileName()
        inPsf = self.inputPSF.get()
        fnInPsf = inPsf.getFileName()
        fnInPoses = self.posesFile.get()
        fnRoot = self._getExtraPath(pwutils.removeBaseExt(fnInVol))
    
        from pyworkflow.em.packages.xmipp3 import getMatlabEnviron
        args=''' -r "diary('%s'); bigfluo_simuFluoParticles3D('%s','%s','%s','%s'); exit"'''%(fnRoot+"_matlab.log",fnInVol,fnInPsf,fnInPoses,fnRoot)
        self.runJob("matlab", args, env=getMatlabEnviron())
 
        dimx = inVol.getDim()[0]
        dimy = inVol.getDim()[1]
        dimz = inVol.getDim()[2]
         
        fnOut = "%s_particles.stk" % fnRoot
        ih = ImageHandler()
        ih.convert("%s_particles.raw#%d,%d,%d,0,float" % (fnRoot,dimx,dimy,dimz,self.nbParticles.get()), fnOut)
         
        outputFluoVol = SetOfFluo3D()
        outputFluoVol.setFileName(fnOut)
         
        self._defineOutputs(outputFluo3D=outputFluoVol)

