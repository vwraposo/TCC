##################################################################################
##                                                                              ##
##  Module to create a report of the results obtained. By using the CADM code   ##
##  to compare the pylogenetic trees obtained with the mtDNA tree.              ##
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
    
    

