# **************************************************************************
# *
# * Authors:     Denis Fortun (denis.fortun@epfl.ch)
# *
# * Biomedical Imgaing Group, EPFL
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

import os
from math import floor
  
import xmipp
from pyworkflow.object import Float
from pyworkflow.utils.path import cleanPath, copyFile, cleanPattern
from pyworkflow.protocol.params import (PointerParam, FloatParam, BooleanParam,
                                        IntParam, StringParam, 
                                        STEPS_PARALLEL, LEVEL_ADVANCED)
from pyworkflow.em.protocol import ProtRefine3D
from pyworkflow.em.data import SetOfClasses2D, Volume
  
from pyworkflow.em.packages.xmipp3.convert import writeSetOfClasses2D, readSetOfVolumes, writeSetOfParticles
from pyworkflow.em.packages.xmipp3.utils import isMdEmpty
from pyworkflow.em.convert import ImageHandler
 
 
class ProtConvMatching(ProtRefine3D):
    """ 
    Computes an initial 3d model from a set of projections/classes 
    using RANSAC algorithm.
     
    This method is based on an initial non-lineal dimensionality
    reduction approach which allows to select representative small 
    sets of class average images capturing the most of the structural 
    information of the particle under study. These reduced sets are 
    then used to generate volumes from random orientation assignments. 
    The best volume is determined from these guesses using a random 
    sample consensus (RANSAC) approach.    
     """
    _label = 'convolution matching test'
     
    def __init__(self, **args):
        ProtRefine3D.__init__(self, **args)
        self.stepsExecutionMode = STEPS_PARALLEL
 
    #--------------------------- DEFINE param functions --------------------------------------------        
    def _defineParams(self, form):
        form.addSection(label='Input')
          
        form.addParam('inputSet', PointerParam, label="Input particles", 
                      pointerClass='SetOfParticles')  
        form.addParam('symmetryGroup', StringParam, default="c1",
                      label='Symmetry group',  
                      help="See http://xmipp.cnb.csic.es/twiki/bin/view/Xmipp/Symmetry"
                           " for a description of the symmetry groups format in Xmipp.\n"
                           "If no symmetry is present, use _c1_.")
        form.addParam('angularSampling', FloatParam, default=5, expertLevel=LEVEL_ADVANCED,
                      label='Angular sampling rate',
                      help='In degrees.'
                      ' This sampling defines how fine the projection gallery from the volume is explored.')
        form.addParam('numIter', IntParam, default=10, expertLevel=LEVEL_ADVANCED,
                      label='Number of iterations to refine the volumes',
                      help='Number of iterations to refine the best volumes using projection matching approach and the input classes')
        form.addParam('initialVolume', PointerParam, label="Initial volume",
                      pointerClass='Volume',
                      help='You may provide a very rough initial volume as a way to constraint the angular search.'
                            'For instance, when reconstructing a fiber, you may provide a cylinder so that side views'
                            'are assigned to the correct tilt angle, although the rotational angle may be completely wrong')           
        form.addParallelSection(threads=8, mpi=1)
             
          
    #--------------------------- INSERT steps functions --------------------------------------------    
    def _insertAllSteps(self):
        self.Xdim = self.inputSet.get().getDimensions()[0]
        self._insertFunctionStep('convertInputStep')
        for it in range(self.numIter.get()):    
            self._insertFunctionStep('projMatchStep')
            self._insertFunctionStep('reconstructStep')
        self._insertFunctionStep('createOutputStep')
     
    #--------------------------- STEPS functions --------------------------------------------
    def convertInputStep(self):
        inputSet = self.inputSet.get()
        fnImgs=self._getExtraPath("imgs.xmd")
        writeSetOfParticles(inputSet, fnImgs)
        imgh = ImageHandler()
        imgh.convert(self.initialVolume.get(),self._getPath("volume.vol"))
              
    def projMatchStep(self):
        fnGallery=self._getExtraPath('gallery.stk')
        fnVolume=self._getPath("volume.vol")
        fnImgs=self._getExtraPath("imgs.xmd")
        fnAngles=self._getExtraPath("angles.xmd")
        self.runJob("xmipp_angular_project_library", "-i %s -o %s --sampling_rate %f --sym %s --method fourier 1 0.25 bspline --compute_neighbors --angular_distance -1 --experimental_images %s"\
                              %(fnVolume,fnGallery,self.angularSampling.get(),self.symmetryGroup.get(),fnImgs))
        self.runJob("xmipp_angular_projection_matching", "-i %s -o %s --ref %s --Ri 0 --Ro %d --max_shift %f --append"\
               %(fnImgs,fnAngles,fnGallery,self.Xdim/2,self.Xdim/2.))
                 
    def reconstructStep(self):
        fnVolume=self._getPath("volume.vol")
        fnAngles=self._getExtraPath("angles.xmd")
        self.runJob("xmipp_reconstruct_fourier","-i %s -o %s --sym %s " %(fnAngles,fnVolume,self.symmetryGroup.get()))
        self.runJob("xmipp_transform_mask","-i %s --mask circular -%d "%(fnVolume,self.Xdim/2)) 
                      
    def createOutputStep(self):
        volume = Volume()
        volume.copyInfo(self.initialVolume.get())
        volume.setFileName(self._getPath('volume.vol'))
        self._defineOutputs(outputVolume=volume)
        self._defineSourceRelation(self.inputSet, volume)
        self._defineSourceRelation(self.initialVolume, volume)
     
    #--------------------------- INFO functions --------------------------------------------
    def _validate(self):
        errors = []
        inputSet = self.inputSet.get()
        if isinstance(inputSet, SetOfClasses2D):
            if not self.inputSet.get().hasRepresentatives():
                errors.append("The input classes should have representatives.")
        return errors
