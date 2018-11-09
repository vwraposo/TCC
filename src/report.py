##################################################################################
##                                                                              ##
##  Module to create a report of the results obtained. By using the CADM code   ##
##  to compare the pylogenetic trees obtained with the mtDNA tree.
##                                                                              ##
##################################################################################
from CADM import CADM
import os 

dirname = '../input/'
directory = os.fsencode(dirname)

gen = dirname + 'genomic/genomic.nex.con.tre'

dont = ['genomic', 'extras', 'de_novo', 'de_novo_HC']

# Compare with others 

print("Report comparing topology using the CADM test of the resulting trees with the tree obtained with the genomic data.")
print(30*("-"))
for d in os.listdir(directory):
    dname = os.fsdecode(d)
    if (not os.path.isdir(dirname + dname)) or (dname in dont):
        continue
    print('Target: ' + dname)
    tree = '{0}{1}/{1}.nex.con.tre'.format(dirname, dname)
    CADM(gen, tree, '-t')

    print(30*("-"))
    
    

