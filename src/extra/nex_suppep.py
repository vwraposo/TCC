##################################################################################
##                                                                              ##
##  Module that gets the identified supporting peptides and creates a NEXUS     ##
##  file without this peptides.                                                 ##
##                                                                              ##
##################################################################################
import os
import middleware as mw
from nexus import NexusWriter

directory = "../reports/supp_peptides/"
records = {}
with open(directory + "char_matrix.txt") as f:
    ids = f.readline().split("\t#")
    ids[0] = ids[0][1:]
    ids[-1] = ids[-1][:-1]
    for line in f: 
        line = line.split()
        records[line[0]] = line[1:]

for file in os.listdir(os.fsencode(directory)):
    filename = os.fsdecode(file)
    if "report" not in filename:
        continue;
    print("Processing: " + filename)

    peptides = []
    with open(directory + filename, 'r') as f:
        f.readline(), f.readline()
        for line in f: 
            peptides.append(ids.index(line.split()[2]))


    new_records = {sp : [peps[x] for x in range(len(peps)) if x not in peptides] for sp, peps in records.items()}
    nw = NexusWriter() 
    for sp in new_records:
        nw.add(sp, 'peptides', 'Standard', ''.join(new_records[sp])), new_records

    name = filename.split('_')[1][:-4]
    nw.writeFile('../input/extras/supp_pep/{0}/{0}.nex'.format(name))
