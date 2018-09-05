##################################################################################
##                                                                              ##
##  Module that insert the genomic data from FASTA files into the database      ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import os
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()
dirname = "../data/genomic"
directory = os.fsencode(dirname)
aliases = ['12S', '16S', 'NADH', 'cytb']
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".faa"): 
        continue;
    print("Processing: " + filename)
    for rec in SeqIO.parse(filename, "fasta"):
        print (rec.id)
        gn_acc = rec.id
        gn_desc = rec.description 
        gn_alias = ''
        for s in aliases:
            if s in gn_desc:
                if s == 'NADH':
                    gn_alias = 'ND4'
                else:
                    gn_alias = s
                break
        if gn_alias == '':
            print("Error: alias not found")
            sys.exit(1)
        gn_seq = rec.seq
        sn_sp = gn_desc.split()[2]
        try:
            cur.execute("INSERT INTO genes(gn_acc, gn_desc, gn_seq, gn_alias, sn_sp) VALUES"
                    "('{0}', '{1}', '{2}', '{3}', '{4}') \
                    ON CONFLICT DO NOTHING;".format(gn_acc, gn_desc, gn_seq, gn_alias, sn_sp))
        except psycopg2.ProgrammingError as e:
            print("Insert error")
            print(e)
            conn.rollback()
            print("Rollback complete")

        conn.commit()

cur.close()
conn.close()
