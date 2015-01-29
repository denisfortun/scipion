# **************************************************************************
# *
# * Authors:    Carlos Oscar Sorzano (coss@cnb.csic.es)
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
# *  e-mail address 'coss@cnb.csic.es'
# *
# **************************************************************************
"""
Consensus picking protocol
"""
import collections
from itertools import izip
from math import sqrt

from pyworkflow.utils.path import cleanPath, removeBaseExt
from pyworkflow.object import Set, Integer, Float, String, Object
import pyworkflow.protocol.params as params
from pyworkflow.em.protocol.protocol_particles import ProtParticlePicking
from pyworkflow.protocol.constants import *
from pyworkflow.em.data import SetOfCoordinates, Coordinate

import pyworkflow.em as em
import convert 
import numpy as np


class XmippProtConsensusPicking(ProtParticlePicking):
    """
    Protocol to estimate the agreement between different particle picking algorithms
    """
    _label = 'consensus picking'
    
    def __init__(self, **args):
        ProtParticlePicking.__init__(self, **args)
        self.stepsExecutionMode = STEPS_PARALLEL

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputCoordinates', params.MultiPointerParam, pointerClass='SetOfCoordinates',
                      label="Input coordinates",
                      help='Select the set of coordinates to compare')
        form.addParam('consensusRadius',params.IntParam, default=10, label="Radius",
                      help="All coordinates within this radius (in pixels) are presumed to correspond to the same particle")
        form.addParam('consensus',params.IntParam, default=-1, label="Consensus", expertLevel=LEVEL_ADVANCED,
                      help="How many times need a particle to be selected to be considered as a consensus particle. "\
                           "Set to -1 to indicate that it needs to be selected by all algorithms. Set to 1 to indicate that "\
                           "it suffices that only 1 algorithm selects the particle")
        form.addParallelSection(threads=4, mpi=1)
        
#--------------------------- INSERT steps functions --------------------------------------------  
    def _insertAllSteps(self):
        deps = []
        for micrograph in self.inputCoordinates[0].get().getMicrographs():
            stepId = self._insertFunctionStep("calculateConsensusStep", 
                                              micrograph.getObjId(), prerequisites=[])
            deps.append(stepId)
        self._insertFunctionStep("createOutputStep", prerequisites=deps)
    
    def _summary(self):
        message = []
        for i, coordinates in enumerate(self.inputCoordinates):
            protocol = self.getMapper().getParent(coordinates.get())
            message.append("Method %d %s" % (i+1, protocol.getClassLabel()))
        message.append("Radius = %d" % self.consensusRadius)
        message.append("Consensus = %d" % self.consensus)
        return message
    
    def _methods(self):
        return []    
    
    def calculateConsensusStep(self, micId):
        # Get all coordinates for this micrograph
        coords = []
        Ncoords = 0
        for coordinates in self.inputCoordinates:
            coordArray = np.asarray([x.getPosition() 
                                     for x in coordinates.get().iterCoordinates(micId)])
            coords.append(coordArray)
            Ncoords += coordArray.shape[0]
        
        allCoords = np.zeros([Ncoords,2])
        votes = np.zeros(Ncoords)
        
        # Add all coordinates in the first method
        N0 = coords[0].shape[0]
        allCoords[0:N0,:] = coords[0]
        votes[0:N0] = 1
        
        # Add the rest of coordinates
        Ncurrent = N0
        for n in range(1, len(self.inputCoordinates)):
            for coord in coords[n]:
                dist = np.sum((coord - allCoords[0:(Ncurrent-1)])**2, axis=1)
                imin = np.argmin(dist)
                if sqrt(dist[imin]) < self.consensusRadius:
                    newCoord = (votes[imin]*allCoords[imin,]+coord)/(votes[imin]+1)
                    allCoords[imin,] = newCoord
                    votes[imin] += 1
                else:
                    allCoords[Ncurrent,:] = coord
                    votes[Ncurrent] = 1
                    Ncurrent += 1
        
        # Select those in the consensus
        if self.consensus <= 0:
            consensus = len(self.inputCoordinates)
        else:
            consensus = self.consensus.get()
        consensusCoords = allCoords[votes>=consensus,:]
        np.savetxt(self._getTmpPath('consensus_%06d.txt' % micId), consensusCoords)
    
    def createOutputStep(self):
        firstCoords = self.inputCoordinates[0].get()
        inputMics = firstCoords.getMicrographs()
        setOfCoordinates = self._createSetOfCoordinates(inputMics)
        setOfCoordinates.setBoxSize(firstCoords.getBoxSize())
        
        # Read all consensus particles
        for micrograph in inputMics:
            fnTmp = self._getTmpPath('consensus_%06d.txt' % micrograph.getObjId())
            coords = np.loadtxt(fnTmp)
            for coord in coords:
                aux = Coordinate()
                aux.setMicrograph(micrograph)
                aux.setX(coord[0])
                aux.setY(coord[1])
                setOfCoordinates.append(aux)
            cleanPath(fnTmp)

        # Set output
        self._defineOutputs(outputCoordinates=setOfCoordinates)
        
        for coordinates in self.inputCoordinates:
            self._defineSourceRelation(coordinates.get(), self.outputCoordinates)