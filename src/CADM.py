##################################################################################
##                                                                              ##
##  Module with the implementation of the CADM test for comparing trees         ##
##  from Campbell 2011                                                          ##
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
import rpy2.robjects as robjects
import dendropy
import numpy as np
import tempfile 
import sys



def CADM (t1, t2, v='-p'):
    if (v == "-t"):
        topo = ''' 
        a <- compute.brlen(a, 1)
        b <- compute.brlen(b, 1)'''
    elif (v == "-p"):
        topo = ''
    else:
        print("Mode not defined")
        raise Exception

    robjects.r('''
        library('ape')
        a <- read.nexus("{0}")
        b <- read.nexus("{1}")
        A <- cophenetic(a)
        {2}
        B <- cophenetic(b)
        x <- rownames(A)
        B <- B[x, x]
        M <- rbind(A, B)
        res.global <- CADM.global(M, 2, Ntip(a))
    '''.format(t1, t2, topo))
    res = robjects.globalenv['res.global']
    print(res)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Wrong number of arguments")
        sys.exit(-1)

    CADM(sys.argv[1], sys.argv[2], sys.argv[3])

