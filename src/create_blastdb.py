import psycopg2
import sys
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna, generic_protein


# Create a fasta file with the Peptides in the database

try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: it was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()
try:
    cur.execute("SELECT * FROM peptides;")
    if cur.rowcount == 0:
        print("Eror: no peptides in the database.")
        raise Exception
except psycopg2.ProgrammingError as e:
    print(e)
    conn.rollback()
    print("Rollback complete")

pid = 0
records = []
for tup in cur:
    records.append(SeqRecord(Seq(tup[0], generic_protein), id="p{0}".format(str(pid).zfill(4)), name='', description=''))
    pid += 1

SeqIO.write(records, '../data/peptides.faa', "fasta")

cur.close()
conn.close()
