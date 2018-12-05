##################################################################################
##   Script to generate reports from de novo peptides trees                     ##
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
import sys

def report(folder):
    dirname = '../input/'
    gen = dirname + 'genomic/genomic.nex.con.tre'

    dirname += folder

    directory = os.fsencode(dirname)


    # Compare with others 

    print("Report comparing topology using the CADM test of the resulting denovo trees with the tree obtained with the genomic data.")
    print(30*("-"))
    for d in os.listdir(directory):
        dname = os.fsdecode(d)
        if (not os.path.isdir(dirname + '/' + dname)):
            continue
        print('Target: ' + dname)
        tree = '{0}/{1}/peptides.nex.con.tre'.format(dirname, dname)
        print(tree)
        CADM(gen, tree, '-p')

        print(30*("-"))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Wrong number of arguments")
        sys.exit(-1)

    report(sys.argv[1])

