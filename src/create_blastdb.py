##################################################################################
##                                                                              ##
##   Module that writes a FASTA file containing all the peptide data for the    ##
##   creation of a BLAST database.                                              ##
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
from subprocess import call
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna, generic_protein


def createFile (query, filename):
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute(query)
        if cur.rowcount == 0:
            print("Error: the query did not return any data.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = []
    for tup in cur:
        records.append(SeqRecord(Seq(tup[1], generic_protein), id="{0}".format(str(tup[0])), name='', description=''))


    fname = '../data/blast/{0}.faa'.format(filename)
    f = open(fname, "w")
    SeqIO.write(records, fname, "fasta")
    f.flush()
    f.close()

    cur.close()
    conn.close()

queries = {}
queries["all_peptides"] = "SELECT DISTINCT p.pep_id, p.pep_seq \
                        FROM peptides AS p, pep_sn AS r \
                        WHERE p.pep_id = r.pep_id;"
queries["peptides"] = "SELECT DISTINCT p.pep_id, p.pep_seq \
                        FROM peptides AS p, pep_sn AS r \
                        WHERE p.pep_id = r.pep_id\
                        AND p.pep_T = 1;"

queries["atrox_peptides"] = "SELECT DISTINCT p.pep_id, p.pep_seq \
                        FROM peptides AS p, pep_at AS r \
                        WHERE p.pep_id = r.pep_id;"

for k in queries:
    createFile(queries[k], k)
    # call("makeblastdb -in ../data/blast/{0}.faa -dbtype prot -out ../data/blast/db/blast/{0} -hash_index".format(k))
