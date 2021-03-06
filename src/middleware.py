##################################################################################
##                                                                              ##
##   Module that workds as a middleware for the program that generates          ##
## the NEXUS file, meaning when the user asks for a type of data the program    ##
## call this module to get the aligned sequences that will go to the NEXUS file ##
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
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna, generic_protein
from Bio.Align.Applications import ClustalOmegaCommandline
from pep_equiv import PepEquiv

# Recieve a type (alias) of gene, then get the sequences from the database and returns the aligned sequences  
def getAlignedSeq(alias):
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM genes WHERE gn_alias = '{0}';".format(alias))
        if cur.rowcount == 0:
            print("Eror: no data with the alias: {0}".format(alias))
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")


    records = []
    for tup in cur:
        records.append(SeqRecord(Seq(tup[2], generic_dna), id=tup[0], name=tup[4], description=tup[1]))

    in_file = tempfile.NamedTemporaryFile()
    out_file = tempfile.NamedTemporaryFile()

    SeqIO.write(records, in_file.name, "fasta")

    clustalomega_cline = ClustalOmegaCommandline(infile=in_file.name, outfile=out_file.name, verbose=True, auto=True, force=True)
    clustalomega_cline()

    records = []
    for record in SeqIO.parse(out_file.name, "fasta"):
        record.seq.alphabet = generic_dna
        records.append(record)

    in_file.close()
    out_file.close()
    cur.close()
    conn.close()

    return records


def getStandard(chset):
    if chset == 'protein':
        return _getProteins('T')
    elif chset == 'lec_protein':
        return _getProteins('L') 
    elif chset == 'all_protein':
        return _getProteins('TL') 
    elif chset == 'peptides':
        return _getPeptides('T')
    elif chset == 'all_peptides':
        return _getPeptides('TL')
    elif chset == 'glycans':
        return _getGlycans()
    else:
        print("Error: charset not defined.")
        raise Exception

# Returns the proteic data from the database in a standard form 
def _getProteins(typ):
    if typ == 'T':
        where = 'AND pr.pr_T = 1' 
    elif typ == 'L':
        where = 'AND (pr.pr_WGA = 1 OR pr.pr_ConA = 1 OR pr.pr_PNA = 1)'
    elif typ == 'TL':
        where = ''
    else:
        print("Error: protein type not defined.")
        raise Exception

    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT r.pr_acc FROM pr_sn AS r, proteins AS pr WHERE pr.pr_acc = r.pr_acc {0};".format(where))
        if cur.rowcount == 0:
            print("Error: there are not proteins in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    proteins = [tup[0] for tup in cur]

    if typ == 'T':
        where = 'AND pr_T = 1' 
    elif typ == 'L':
        where = 'AND (pr_WGA = 1 OR pr_ConA = 1 OR pr_PNA = 1)'
    elif typ == 'TL':
        where = ''


    try:
        cur.execute("SELECT DISTINCT * FROM pr_sn, proteins WHERE pr_sn.pr_acc = proteins.pr_acc {0};".format(where))
        if cur.rowcount == 0:
            print("Eror: there are not proteins related to species in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if tup[0] not in records:
            records[tup[0]] = [str(0)] * len(proteins)  

        summ = 1
        if typ == 'L' or typ == 'TL':
            summ = sum(tup[4:])
        records[tup[0]][proteins.index(tup[1])] = str(summ)

    cur.close()
    conn.close()
    return records

# Returns the proteic data from the database in a binary form 
def _getPeptides(typ=''):

    if typ == "T":
        where =  ", peptides AS e WHERE e.pep_id = r.pep_id AND  e.pep_T = 1"
        db = "peptides"
    elif typ == "TL":
        where = ""
        db = "all_peptides"

    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)
    cur = conn.cursor()

    try:

        cur.execute("SELECT DISTINCT r.pep_id FROM pep_sn AS r {0};".format(where))
        if cur.rowcount == 0:
            print("Error: there are not peptides in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    peptides = [tup[0] for tup in cur]

    equiv = PepEquiv(peptides)
    equiv.run(db)
   
    classes = equiv.getClasses()

    if typ == "T":
        where =  "AND e.pep_T = 1"
    elif typ == "TL":
        where = ""

    try:
        cur.execute("SELECT DISTINCT * FROM pep_sn AS r, peptides AS e WHERE e.pep_id = r.pep_id {0};".format(where))
        if cur.rowcount == 0:
            print("Eror: there are not peptides related to species in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if tup[1] not in records:
            records[tup[1]] = [str(0)] * len(classes)  
        
        f = equiv.getRep(tup[0])
        summ = 1
        if typ == 'TL':
            summ = sum(tup[4:])
        records[tup[1]][classes.index(f)] = str(summ)

    cur.close()
    conn.close()

    return records

# Returns the N-glycan data from the database in a binary form 
def _getGlycans():
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT gl_id FROM gl_sn;")
        if cur.rowcount == 0:
            print("Error: there are not glycans in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    glycans = [tup[0] for tup in cur]
    try:
        cur.execute("SELECT DISTINCT * FROM gl_sn;")
        if cur.rowcount == 0:
            print("Eror: there are not glycans related to species in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if tup[1] not in records:
            records[tup[1]] = [str(0)] * len(glycans)  

        records[tup[1]][glycans.index(tup[0])] = str(1)

    cur.close()
    conn.close()
    

    return records


