##################################################################################
##                                                                              ##
##  Module with the implementation of the Union Find data structure             ##
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

