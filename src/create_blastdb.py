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

records = []
for tup in cur:
    records.append(SeqRecord(Seq(tup[1], generic_protein), id="{0}".format(str(tup[0])), name='', description=''))

SeqIO.write(records, '../data/blast/peptides.faa', "fasta")

cur.close()
conn.close()
