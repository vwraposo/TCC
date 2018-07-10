import dendropy
import numpy as np


# Nao parece certo adicionar uma constante

# O algoritmo de decomposicao parece estranho

# NISI da entre 0 e 1?

class LL:

    def __init__(self, t1, t2, f="nexus"):
        tns = dendropy.TaxonNamespace()

        self.tree1 = dendropy.Tree.get_from_path(t1, f, taxon_namespace=tns)
        self.n = len(self.tree1.taxon_namespace)
        self.dm1 = self._getDistanceMatrix(self.tree1, f)
        a = self._getDecomposition(self.dm1)

        self.tree2 = dendropy.Tree.get_from_path(t2, f, taxon_namespace=tns)
        self.dm2 = self._getDistanceMatrix(self.tree2, f)
        a = self._getDecomposition(self.dm2)


    def _getDistanceMatrix(self, tree, f):
        pdm = dendropy.calculate.treemeasure.PatrisiticDistanceMatrix(tree)
        dm = []
        for tax1 in tree.taxon_namespace:
            dm.append(list(map(lambda tax2: pdm(tax1, tax2), tree.taxon_namespace))) 
        
        # Make matrix values between 0, 1
        dm = np.array(dm)
        return dm

    def _getDecomposition(self, dm):

        # Finding center
        c = 0
        mn = np.sum(dm[c])
        for i in range(1, self.n):
            s = np.sum(dm[i])
            if s < mn: 
                c = i 
                mn = s

        radius = np.min(dm[dm != np.min(dm)])
        U = dm.copy()
        for i in range(self.n):
            for j in range(self.n):
                if i == j: 
                    continue;
                U[i][j] = U[i][j] - (dm[c][i] - radius) - (dm[c][j] - radius)


        C = dm - U
        # Check negatives, sum constant
        
        return U, C

    def _standardize(self, m):
        return m / np.max(m)

    def NISI(self):
        result = 0
        for i in range(self.n):
            for j in range(self.n):
                Cu = 1 - max(self.dm1[i][j], self.dm2[i][j])
                Co = abs(self.dm1[i][j] - self.dm2[i][j]) 
                MX = max(Cu, Co)
                result += (Cu - Co) /  MX
        return (1 + result) / 2

    def SSD(self):
        return np.sum((self.dm1-self.dm2)**2)

# Gera Arvores aleatorias 

# Obtem a probabilidade 

ll = LL('t1.nex', 't2.nex')
