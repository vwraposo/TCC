##################################################################################
##                                                                              ##
##   Module write NEXUS files for B. atrox data                                 ##
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
