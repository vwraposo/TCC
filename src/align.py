##################################################################################
##                                                                              ##
##   Module that will recieve a type (alias) of mtDNA, then get the sequences   ##
##  from the database and returns the aligned sequences                         ##
##  It will work as a middleware for the program that generates the NEXUS file, ##
##  meaning when the user asks for a type of data the program call this         ##
##  module to get the aligned sequences that will go to the NEXUS file          ##
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
from Bio.Alphabet import generic_dna

def getAlignedSeq (alias):
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("It was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    # Fluxo: Construir arquivo fasta a apartir do DB, chamr clustalo, deletar arquivos FXSTXtry:
    try:
        cur.execute("SELECT * FROM mtdnas WHERE mt_alias = '{0}';".format(alias))
        if cur.rowcount == 0:
            print("No data with the alias: {0}".format(alias))
            sys.exit(1)
    except psycopg2.ProgrammingError as e:
        print("Insert error")
        print(e)
        conn.rollback()
        print("Rollback complete")


    records = []
    for tup in cur:
        records.append(SeqRecord(Seq(tup[2], generic_dna), id=tup[0], description=tup[1]))

    in_file = tempfile.NamedTemporaryFile()
    out_file = tempfile.NamedTemporaryFile()

    SeqIO.write(records, in_file.name, "fasta")

    clustalomega_cline = ClustalOmegaCommandline(infile=in_file.name, outfile=out_file.name, verbose=True, auto=True, force=True)
    clustalomega_cline()

    records = []
    for record in SeqIO.parse(out_file.name, "fasta"):
        records.append(record)

    in_file.close()
    out_file.close()
    cur.close()
    conn.close()

    return records


records = getAlignedSeq("ND4")
for rec in records:
    print(rec)
    print()

