import rpy2.robjects as robjects
import dendropy
import numpy as np
import tempfile 

# def getDistanceMatrix(t, f="nexus"):
    # """ Description

    # Parameters
    # ----------

    # Returns
    # ----------
    # """

    # tns = dendropy.TaxonNamespace()
    # tree = dendropy.Tree.get_from_path(t, f, taxon_namespace=tns)
    # pdm = dendropy.calculate.treemeasure.PatrisiticDistanceMatrix(tree)
    # A = []
    # for tax1 in tree.taxon_namespace:
        # A.append(list(map(lambda tax2: pdm(tax1, tax2), tree.taxon_namespace))) 
    
    # # Make matrix values between 0, 1
    # A = np.array(A)
    # return A

# def _checkDMatrix(A):
    # if not np.allclose(A, A.T):
        # raise Exception
    # n, m = np.shape(A)
    # if (n != m):
        # raise Exception

# def _checkDMatrixes(A, B):
    # _checkDMatrix(A) 
    # _checkDMatrix(B) 

    # nA, m = np.shape(A)
    # nB, m = np.shape(B)
    # if (nA != nB):
        # raise Exception

# def writeFile(A, name):
    # for i in A: 
        # print(" ".join(list(map(lambda x: str(x), i))))


def CADM (t1, t2):
    # Creates distance matrix files
    # A = getDistanceMatrix(t1)
    # _checkDMatrix(A)
    # B = getDistanceMatrix(t2)
    # _checkDMatrix(B)
    # _checkDMatrixes(A, B)
    # # x <- rownames(A)
    # B <- B[x, x]
    # M <- rbind(A, B)
    # Run CADM from the R package 
    robjects.r('''
        library('ape')
        a <- read.nexus("{0}")
        b <- read.nexus("{1}")
        A <- cophenetic(a)
        B <- cophenetic(b)
        x <- rownames(A)
        B <- B[x, x]
        M <- rbind(A, B)
        res.global <- CADM.global(M, 2, Ntip(a))
    '''.format(t1, t2))
    res = robjects.globalenv['res.global']
    print(res)

CADM("../test/t1.nex", "../test/t2.nex")
# lec_protein all_protein
CADM("../test/t3.nex", "../test/t4.nex")
CADM("../input/mithocondrial/molecular.nex.con.tre", "../test/t4.nex")
