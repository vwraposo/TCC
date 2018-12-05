##################################################################################
##                                                                              ##
##   Module write NEXUS files for B. atrox data                                 ##
##                                                                              ##
##   This file is part of the featsel program                                   ##
##   Copyright (C) 2018 Victor Wichmann Raposo                                  ##
##                                                                              ##
##   This program is free software: you can redistribute it and/or modify       ##
##   it under the terms of the GNU General Public License as published by       ##
##   the Free Software Foundation, either version 3 of the License, or          ##
##   (at your option) any later version.                                        ##
##                                                                              ##
##   This program is distributed in the hope that it will be useful,            ##
##   but WITHOUT ANY WARRANTY; without even the implied warranty of             ##
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              ##
##   GNU General Public License for more details.                               ##
##                                                                              ##
##   You should have received a copy of the GNU General Public License          ##
##   along with this program.  If not, see <http://www.gnu.org/licenses/>.      ##
##                                                                              ##
##################################################################################

import atrox_middleware as mw
from nexus import NexusWriter
from Bio import SeqIO
import cmd
import psycopg2


nwR = NexusWriter()

records = mw.getPeptides("R")
for rec in records:
    nwR.add(rec, 'peptides', 'Standard', "".join(records[rec]))

nwR.writeFile("../input/extras/atrox/pep_Rep.nex")

nw = NexusWriter() 
records = mw.getPeptides()
for rec in records:
    nw.add(rec, 'peptides', 'Standard', "".join(records[rec]))

nw.writeFile("../input/extras/atrox/pep.nex")
