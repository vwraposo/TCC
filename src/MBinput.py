##################################################################################
##                                                                              ##
##   Module that lets a user choose the data from the database and then         ##
##   builds a nexus file that will be the input for MrBayes.                    ##
##                                                                              ##
##################################################################################
import align as al
from nexus import NexusWriter
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna

records = al.getAlignedSeq('16S') 
n = NexusWriter()
for rec in records:
    n.add(rec.description.split()[2], '16S', 'DNA', str(rec.seq))
    n.add(rec.description.split()[2], 'morph', 'Standard', '01002010010300405032110123')
records = al.getAlignedSeq('ND4') 
for rec in records:
    n.add(rec.description.split()[2], 'ND4', 'DNA', str(rec.seq))
n.writeFile("out")

