# **************************************************************************
# *
# * Authors:     Denis Fortun (denis.fortun@epfl.ch)
# *
# * Biomedical Imaging Group EPFL
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
This sub-package contains data and protocol classes
wrapping EPFL Fluorescence routines
"""
from bibtex import _bibtex # Load bibtex dict with references

_logo = "psf_logo.png"

from epfl import *

from data import Fluo3D, SetOfFluo3D

_environ = getEnviron()

# from viewer import *
from protocol_import_fluo3D import ProtImportFluo3D
from protocol_fluorescence_convolutionMatching import ProtConvMatching
from protocol_ransac_fluo import ProtRansacFluo
from protocol_extract_particles_3D import ProtExtractParticles3D
from pyworkflow.em.packages.xmipp3.protocol_cltomo import XmippProtCLTomo
from protocol_align_3D import ProtAlign3D
from protocol_create_mask3d_fluo import XmippProtCreateMask3DFluo
from protocol_create_set_of_micrographs_fluo import ProtCreateSetMicFluo
from protocol_convolution3D import ProtConvolution3D
from protocol_average3D import ProtAverage3D
from protocol_simu_fluo_particles3D import ProtSimuFluoParticles3D
from protocol_apply_classif_align import ProtApplyClassAlign2D
from protocol_apply_classif_align_3D import ProtApplyClassAlign3D
from protocol_apply_alignment_3D import ProtApplyAlignment3D
from protocol_apply_pose_2D import ProtApplyPose2D
from protocol_convolution_matching import ProtConvMatch
from protocol_reconstruct_admm import ProtReconstructADMM
