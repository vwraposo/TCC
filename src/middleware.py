##################################################################################
##                                                                              ##
##   Module that will work as a middleware for the program that generates       ##
## the NEXUS file, meaning when the user asks for a type of data the program    ##
## call this module to get the aligned sequences that will go to the NEXUS file ##
##                                                                              ##
##################################################################################
import psycopg2
from subprocess import call
import sys
import tempfile 
from Bio.Align.Applications import ClustalOmegaCommandline
from subprocess import call
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna, generic_protein

# Recieve a type (alias) of mtDNA, then get the sequences from the database and returns the aligned sequences  
def getAlignedSeq(alias):
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM mtdnas WHERE mt_alias = '{0}';".format(alias))
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
        return _getProteins('Total')
    elif chset == 'lec_protein':
        return _getProteins('Lectins') 
    else:
        print("Error: charset not defined.")
        raise Exception

# Returns the proteic data from the database in a standard form 
def _getProteins(typ):
    if typ == 'Total':
        where = 'WHERE pr_T = 1' 
    elif typ == 'Lectins':
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
        cur.execute("SELECT DISTINCT pr_acc FROM proteins {0};".format(where))
        if cur.rowcount == 0:
            print("Error: there are no proteins in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    proteins = [tup[0] for tup in cur]

    if typ == 'Total':
        where = 'AND pr_T = 1' 
    elif typ == 'Lectins':
        where = ''

    try:
        cur.execute("SELECT DISTINCT * FROM pr_sn, proteins WHERE pr_sn.pr_acc = proteins.pr_acc {0};".format(where))
        if cur.rowcount == 0:
            print("Eror: there are no proteins in the database.")
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
        if typ == 'Lectins':
            summ = sum(tup[4:])
        records[tup[0]][proteins.index(tup[1])] = str(summ)
    
    return records

# Returns the peptidic data from the database in a binary form 
# def getPeptides():






