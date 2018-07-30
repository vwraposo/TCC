import rpy2.robjects as robjects
import dendropy
import numpy as np
import tempfile 
import sys

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Too many arguments")
        sys.exit(-1)

    CADM(sys.argv[1], sys.argv[2], sys.argv[3])

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

# CADM("../test/t1.nex", "../test/t2.nex", "-t")
# # lec_protein all_protein
# CADM("../test/t3.nex", "../test/t4.nex" )
# CADM("../input/mithocondrial/molecular.nex.con.tre", "../test/t4.nex")
