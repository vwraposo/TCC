##################################################################################
##                                                                              ##
##   Module that will to create nexus files with the data from B. atrox         ##
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
import psycopg2
import sys
import tempfile 
import cmd
from nexus import NexusWriter
from UF import UnionFind 
from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast import NCBIXML

MAX_DIFF = 2
MAX_HITS = 5
MIN_SCORE = 20 
MIN_EVALUE = 1e-05

try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: it was not possible to connect to the database")
    sys.exit(1)
cur = conn.cursor()

try:

    cur.execute("SELECT DISTINCT pep_id FROM pep_at;")
    if cur.rowcount == 0:
        print("Error: there are not peptides in the database.")
        raise Exception
except psycopg2.ProgrammingError as e:
    print(e)
    conn.rollback()
    print("Rollback complete")

peptides = [tup[0] for tup in cur]
n_pep = len(peptides)
dic = dict(zip(peptides, range(n_pep)))
dicI = dict(zip(range(n_pep), peptides))

uf = UnionFind(n_pep)

out_file = tempfile.NamedTemporaryFile()
blastp_cline = NcbiblastpCommandline(query="../data/blast/atrox_peptides.faa", db="../data/blast/db/atrox_peptides", evalue=MIN_EVALUE, threshold=MIN_SCORE, max_target_seqs=MAX_HITS, num_threads = 3, outfmt=5, out=out_file.name)
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
        if abs(len_t - len_r) <= MAX_DIFF and pid_t != pid_r:
            if (pid_t not in dic): 
                print("Error: BLAST database not congruent with local database")
                sys.exit(1)
            if (pid_r in dic):
                uf.union (dic[pid_t], dic[pid_r])
            break


classes  = list(filter(lambda x: dic[x] == uf.find(dic[x]), peptides))

def getPeptides(typ=''):
    try:
        if typ == "R":
            cur.execute("SELECT DISTINCT r.pep_id, at.at_habitat, at.at_replicate \
                    FROM pep_at AS r, atrox AS at \
                    WHERE r.at_id = at.at_id;")
        else:
            cur.execute("SELECT DISTINCT r.pep_id, at.at_habitat \
                    FROM pep_at AS r, atrox AS at \
                    WHERE r.at_id = at.at_id;")
            if cur.rowcount == 0:
                print("Eror: there are not peptides related to species in the database.")
                raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if typ == "R":
            k = "{0}_{1}".format(tup[1], tup[2])
        else:
            k = tup[1]
        if k not in records:
            records[k] = [str(0)] * len(classes)  

        f = dicI[uf.find(dic[tup[0]])]
        records[k][classes.index(f)] = str(1) 

    out_file.close()

    return records

nwR = NexusWriter()

records = getPeptides("R")
for rec in records:
    nwR.add(rec, 'peptides', 'Standard', "".join(records[rec]))

nwR.writeFile("../input/extras/atrox/pep_Rep.nex")

nw = NexusWriter() 
records = getPeptides()
for rec in records:
    nw.add(rec, 'peptides', 'Standard', "".join(records[rec]))

nw.writeFile("../input/extras/atrox/pep.nex")

cur.close()
conn.close()
