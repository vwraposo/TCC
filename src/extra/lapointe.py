import dendropy
import numpy as np


# Nao parece certo adicionar uma constante

# O algoritmo de decomposicao parece estranho

# NISI da entre 0 e 1?

# NISI divide por 0?
def _checkDMatrix(A):
    if not np.allclose(A, A.T):
        raise Exception
    n, m = np.shape(A)
    if (n != m):
        raise Exception

def _checkDMatrixes(A, B):
    _checkDMatrix(A) 
    _checkDMatrix(B) 

    nA, m = np.shape(A)
    nB, m = np.shape(B)
    if (nA != nB):
        raise Exception

def standardize(A):
    _checkMatrix(A)
    """ Compute matrix with values in [0, 1]

    Parameters
    ----------
    A: np.array, 
        distance matrix

    Returns
    ----------
    B: np.array, 
        standardized matrix
    """
    return A / np.max(A)

def getDecomposition(A):
    """ Compute the decomposition of a distance matrix into the matrix of
    the ultrametric tree and the matrix of the star tree

    Parameters
    ----------
    A: np.array, 
        distance matrix
    
    Returns
    ----------
    U: np.array, 
        distance matrix of the ultrametric tree

    C: np.array, 
        distance matrix of the star tree
    """
    _checkDMatrix(A)
    n, m = np.shape(A)
    # Finding center
    c = 0
    mn = np.sum(A[c])
    for i in range(1, n):
        s = np.sum(A[i])
        if s < mn: 
            c = i 
            mn = s

    radius = np.min(A[A != np.min(A)])
    U = A.copy()
    for i in range(n):
        for j in range(n):
            if i == j: 
                continue;
            U[i][j] = U[i][j] - (A[c][i] - radius) - (A[c][j] - radius)


    C = A - U
    # Check negatives, sum constant
    
    return U, C

def NISI(A, B):
    """ Description

    Parameters
    ----------

    Returns
    ----------
    """
    _checkDMatrixes(A, B) 
    n, m = np.shape(A)
    result = 0
    for i in range(n):
        for j in range(n):
            if j == i:
                continue
            Cu = 1 - max(A[i][j], B[i][j])
            Co = abs(A[i][j] - B[i][j]) 
            MX = max(Cu, Co)
            result += (Cu - Co) /  MX
    return (1 + result) / 2

def SSD(A, B):
    """ Description

    Parameters
    ----------

    Returns
    ----------
    """
    _checkDMatrixes(A, B) 
    return np.sum((A-B)**2)

def getDistanceMatrix(t, f):
    """ Description

    Parameters
    ----------

    Returns
    ----------
    """

    tns = dendropy.TaxonNamespace()
    tree = dendropy.Tree.get_from_path(t, f, taxon_namespace=tns)
    pdm = dendropy.calculate.treemeasure.PatrisiticDistanceMatrix(tree)
    A = []
    for tax1 in tree.taxon_namespace:
        A.append(list(map(lambda tax2: pdm(tax1, tax2), tree.taxon_namespace))) 
    
    # Make matrix values between 0, 1
    A = np.array(A)
    return A




class LL:
    """ Implementation of the metric of comparison between phylogenetic trees
    in the Legendre and Lapointe 1992 paper.

    Parameters
    ----------

    t1: string, 
        name of a file with a phylogenetic tree

    t2: string, 
        name of a file with a phylogenetic tree

    f: string, default: nexus, 
        type of file containing the pyhologenetic tree

    """

    def __init__(self, t1, t2, f="nexus"):
        self.dm1 = getDistanceMatrix(t1, f)
        self.dm2 = getDistanceMatrix(t2, f)

        _checkDMatrixes(self.dm1, self.dm2)
        a = getDecomposition(self.dm1)
        b = getDecomposition(self.dm2)



    
# Gera Arvores aleatorias 

# Obtem a probabilidade 

ll = LL('t1.nex', 't2.nex')
