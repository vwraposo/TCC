##################################################################################
##                                                                              ##
##   Module that establishes the equivalence relationship among peptides, using ##
##   Union Find and one-against-all BLAST                                       ##
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

from UF import UnionFind 
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast import NCBIXML
import tempfile 

class PepEquiv:

    def __init__ (self, peptides):
        self.peptides = peptides
        self.n_pep = len(peptides)
        self.uf = UnionFind(self.n_pep)
        # pep_id -> uf_id
        self.dic = dict(zip(peptides, range(self.n_pep)))
        # uf_id -> pep_id
        self.dicI = dict(zip(range(self.n_pep), peptides))
        self.classes = []
        self.MAX_DIFF = 2
        self.MAX_HITS = 5
        self.MIN_EVALUE = 1e-5

    def setParams(self, diff = 2, hits = 5, evalue = 1e-5):
        self.MAX_DIFF = diff
        self.MAX_HITS = hits
        self.MIN_EVALUE = evalue

    def run(self, db):
        out_file = tempfile.NamedTemporaryFile()
        blastp_cline = NcbiblastpCommandline(query="../data/blast/{0}.faa".format(db), db="../data/blast/db/{0}".format(db), evalue= self.MIN_EVALUE, num_threads = 4, outfmt=5, out=out_file.name)
        print("BLAST started....")
        blastp_cline()
        print("BLAST completed.")


        result_handle = open(out_file.name)
        blast_records = NCBIXML. parse(result_handle)
        for blast_record in blast_records:
            pid_t = int(blast_record.query)
            len_t = blast_record.query_letters
            for al in blast_record.alignments:
                pid_r = int(al.title.split()[-1])
                len_r = al.length
                if abs(len_t - len_r) <= self.MAX_DIFF and pid_t != pid_r:
                    if (pid_t not in self.dic): 
                        print("Error: BLAST database not congruent with local database: " + str(pid_t))
                        sys.exit(1)
                    if (pid_r in self.dic):
                        self.uf.union (self.dic[pid_t], self.dic[pid_r])
                    break 

        self.classes  = list(filter(lambda x: self.dic[x] == self.uf.find(self.dic[x]), self.peptides))
        out_file.close()

    def getClasses(self):
        return self.classes

    def getRep(self, pep_id):
        return self.dicI[self.uf.find(self.dic[pep_id])]

    def writeFile(self, filename):
        with open(filename, "w") as f: 
            for pep in self.peptides:
                f.write("{0}:{1}\n".format(pep, self.uf.find(self.dic[pep])))
