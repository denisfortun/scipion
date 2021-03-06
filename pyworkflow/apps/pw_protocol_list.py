#!/usr/bin/env python
# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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
List all existing protocols within Scipion
"""

import sys
from pyworkflow.em import getProtocols


if __name__ == '__main__':
    count = 0
    withDoc = '--with-doc' in sys.argv
    emProtocolsDict = getProtocols()
    
    protDict = {}
    
    # Group protocols by package name
    for k, v in emProtocolsDict.iteritems():
        packageName = v.getClassPackageName()
        
        if packageName not in protDict:
            protDict[packageName] = []
        
        protDict[packageName].append((k, v))
           
         
    for group, prots in protDict.iteritems():
        print "-" * 100
        print "Package: ", group, "(%d protocols)" % len(prots)
        for k, v in prots:
            print "   %s ( %s )" % (k, v.getClassLabel())
            if withDoc:
                print "      doc: ", v.__doc__
            #count += 1
            
