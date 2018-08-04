##################################################################################
##                                                                              ##
##  Module with the implementation of the CADM test for comparing trees         ##
##  from Campbell 2011                                                          ##
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

