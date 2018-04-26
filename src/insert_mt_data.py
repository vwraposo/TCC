##################################################################################
##                                                                              ##
##  Module that insert the data from FASTA files into the database              ##
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
    print("It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()
dirname = "../data/mtDNA"
directory = os.fsencode(dirname)
aliases = ['12S', '16S', 'NADH', 'cytb']
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".faa"): 
        continue;
    print("Processing: " + filename)
    for rec in SeqIO.parse(filename, "fasta"):
        print (rec.id)
        mt_acc = rec.id
        mt_desc = rec.description 
        mt_alias = ''
        for s in aliases:
            if s in mt_desc:
                if s == 'NADH':
                    mt_alias = 'ND4'
                else:
                    mt_alias = s
                break
        if mt_alias == '':
            print("Error alias not found")
            sys.exit(1)
        mt_seq = rec.seq
        sn_sp = mt_desc.split()[2]
        try:
            cur.execute("INSERT INTO mtDNAs(mt_acc, mt_desc, mt_seq, mt_alias, sn_sp) VALUES"
                    "('{0}', '{1}', '{2}', '{3}', '{4}');".format(mt_acc, mt_desc, mt_seq, mt_alias, sn_sp))
        except psycopg2.ProgrammingError as e:
            print("Insert error")
            print(e)
            conn.rollback()
            print("Rollback complete")

        conn.commit()

cur.close()
conn.close()
