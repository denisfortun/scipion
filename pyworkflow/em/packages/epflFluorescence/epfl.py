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
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
"""
This sub-package contains data and protocol classes
wrapping EPFL Fluorescnce
"""
import os

from pyworkflow.utils import Environ



def getEnviron():
    """ Create the needed environment for EPFL programs. """
    from pyworkflow.em.packages.xmipp3 import getEnviron as xmippGetEnviron
    return xmippGetEnviron()
#     environ = Environ(os.environ)
#     SIMPLEBIN = os.path.join(os.environ['SIMPLE_HOME'], 'bin')
#     environ.update({
#                     'SIMPLEBIN': SIMPLEBIN,
#                     'SIMPLEPATH': os.environ['SIMPLE_HOME'],
#                     'SIMPLESYS': os.environ['SIMPLE_HOME'],
#                     'PATH': SIMPLEBIN + os.pathsep + os.path.join(os.environ['SIMPLE_HOME'], 'apps')
#                     }, 
#                    position=Environ.BEGIN)
#     return environ
