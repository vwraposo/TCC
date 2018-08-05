##################################################################################
##                                                                              ##
##  Module to create a report of the results obtained. By using the CADM code   ##
##  to compare the pylogenetic trees obtained with the mtDNA tree.
##                                                                              ##
##################################################################################
from CADM import CADM
import os 

dirname = '../input/extras/1-out/'
directory = os.fsencode(dirname)


# Compare with others 

print("Report comparing topology using the CADM test of the resulting trees \n (with one snake species missing) with the tree obtained with the mithocondrial data.")
print(30*("-"))
for d in os.listdir(directory):
    dname = os.fsdecode(d)
    if (not os.path.isdir(dirname + dname)):
        print(dname)
        continue
    print('Target: ' + dname)
    mith = '{0}{1}/mithocondrial.nex.con.tre'.format(dirname, dname)
    tree = '{0}{1}/peptides.nex.con.tre'.format(dirname, dname)
    CADM(mith, tree, '-t')

    print(30*("-"))
    
    

