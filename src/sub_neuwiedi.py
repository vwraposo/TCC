##################################################################################
##                                                                              ##
##  Script to create Nexus files with neuwiedi subespecies.                     ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import os
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from nexus import NexusWriter
import middleware as mw

try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()
# Get original data
try:
    cur.execute("SELECT * FROM mtDNAs WHERE "
            "sn_sp='neuwiedi' AND (mt_alias='ND4' OR mt_alias='cytb');")
except psycopg2.ProgrammingError as e:
    print("Insert error")
    print(e)
    conn.rollback()
    print("Rollback complete")

    conn.commit()
old_rec = []
for tup in cur: 
    old_rec.append(tup)

dirname = "../data/mtDNA/sub_neuwiedi"
directory = os.fsencode(dirname)
aliases = ['NADH', 'cytb']
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".faa"): 
        continue;
    print("Processing: " + filename)
    # Delete old data
    try:
        cur.execute("DELETE FROM mtDNAs WHERE "
                "sn_sp='neuwiedi' AND (mt_alias='ND4' OR mt_alias='cytb');")
    except psycopg2.ProgrammingError as e:
        print("Insert error")
        print(e)
        conn.rollback()
        print("Rollback complete")

        conn.commit()


    # Insert new data
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
            print("Error: alias not found")
            sys.exit(1)
        mt_seq = rec.seq
        sn_sp = 'neuwiedi'
        try:
            cur.execute("INSERT INTO mtDNAs(mt_acc, mt_desc, mt_seq, mt_alias, sn_sp) VALUES"
                    "('{0}', '{1}', '{2}', '{3}', '{4}');".format(mt_acc, mt_desc, mt_seq, mt_alias, sn_sp))
        except psycopg2.ProgrammingError as e:
            print("Insert error")
            print(e)
            conn.rollback()
            print("Rollback complete")

        conn.commit()

    # Crete Nexux file
    nwriter = NexusWriter()
    print("Writing: " + "../input/sub_neuwiedi/{0}.nex".format(os.fsdecode(file)[:-4]))
    for s in ['ND4', 'cytb']:
        records = mw.getAlignedSeq(s)
        for rec in records:
            nwriter.add(rec.description.split()[2], s, 'Codon', str(rec.seq))
    nwriter.writeFile("../input/sub_neuwiedi/{0}.nex".format(os.fsdecode(file)[:-4]))

# Restore original data
try:
    cur.execute("DELETE FROM mtDNAs WHERE "
            "sn_sp='neuwiedi' AND (mt_alias='ND4' OR mt_alias='cytb');")
except psycopg2.ProgrammingError as e:
    print("Insert error")
    print(e)
    conn.rollback()
    print("Rollback complete")

    conn.commit()

for tup in old_rec: 
    try:
        cur.execute("INSERT INTO mtDNAs(mt_acc, mt_desc, mt_seq, mt_alias, sn_sp) VALUES"
                "('{0}', '{1}', '{2}', '{3}', '{4}');".format(tup[0], tup[1], tup[2], tup[3], tup[4]))
    except psycopg2.ProgrammingError as e:
        print("Insert error")
        print(e)
        conn.rollback()
        print("Rollback complete")

    conn.commit()

cur.close()
conn.close()



