##################################################################################
##                                                                              ##
##  Script to create a Nexus file with all the neuwiedi subespecies.            ##
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



new_sp = []
dirname = "../data/mtDNA/sub_neuwiedi"
directory = os.fsencode(dirname)
aliases = ['NADH', 'cytb']
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".faa"): 
        continue;
    print("Processing: " + filename)
 

    try:
        cur.execute("INSERT INTO snakes(sn_sp, sn_ge) VALUES ('{0}', 'Bothrops');".format(os.fsdecode(file)[:-4]))
    except psycopg2.ProgrammingError as e:
        print("Insert error")
        print(e)
        conn.rollback()
        print("Rollback complete")

    conn.commit()

    new_sp.append(os.fsdecode(file)[:-4])
    # Insert new data as new species
    for rec in SeqIO.parse(filename, "fasta"):
        print (rec.id)
        mt_acc = rec.id
        mt_desc = rec.description.replace('neuwiedi', '')
        print(mt_desc)
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

# Crete Nexux file
nwriter = NexusWriter()
print("Writing: file")
for s in ['ND4', 'cytb']:
    records = mw.getAlignedSeq(s)
    for rec in records:
        nwriter.add(rec.description.split()[2], s, 'Codon', str(rec.seq))
nwriter.writeFile("FILE.nex") #("../input/sub_neuwiedi/sub_neuwiedi.nex") 

# Restore original data
for s in new_sp:
    try:
        cur.execute("DELETE FROM snakes WHERE sn_sp = '{0}';".format(s))
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



