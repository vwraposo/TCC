##################################################################################
##                                                                              ##
##  Module with the implementation of the Union Find data structure             ##
##                                                                              ##
##################################################################################
class UnionFind:

    def __init__ (self, n):
        self.id = list(range(n))
        self.sz = [1] * n

    def find(self, p):
        f = self.id[p] 
        if (f == p):
            return p;
        self.id[p] = self.find(f)
        return self.id[p]

    def union(self, p, q):
        p = self.find(p)
        q = self.find(q)
        if (p == q):
            return
        if (self.sz[p] > self.sz[q]):
            p, q = q, p 
        self.id[p] = q
        self.sz[q] += self.sz[p]

