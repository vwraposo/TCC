##################################################################################
##                                                                              ##
##  Module that insert the protein and peptide data from csv files              ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import os
import csv


try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()

## Total Proteins
dirname = "../data/protein"
directory = os.fsencode(dirname)
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".csv"): 
        continue;
    print("Processing: " + filename)

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        
        species = str(file).split()[1][:-5]
        protein = ''
        toxclass = ''
        for row in reader:
            if row['Accession number'] != '' and row['Toxin Class'] != '':
                protein = row['Accession number'].strip()
                toxclass = row['Toxin Class']

                # New Protein 
                for pr in protein.split(','):
                    pr = pr.strip()
                    try:
                        cur.execute("INSERT INTO proteins(pr_acc, pr_toxclass, pr_T) VALUES ('{0}', '{1}', 1)\
                                ON CONFLICT DO NOTHING;".format(pr, toxclass))
                        cur.execute("INSERT INTO pr_sn(pr_acc, sn_sp) VALUES ('{0}', '{1}')\
                                ON CONFLICT DO NOTHING;".format(pr, species))
                    except psycopg2.ProgrammingError as e:
                        print("Insert error")
                        print(e)
                        conn.rollback()
                        print("Rollback complete")

                    conn.commit()

            # Add Peptide
            peptide = row['Peptides'].upper()
            if (peptide == ''): 
                continue;
            for pr in protein.split(','):
                pr = pr.strip()
                try:
                    cur.execute("SELECT pep_id FROM peptides WHERE pep_seq = '{0}';".format(peptide))
                    if (cur.rowcount == 0):
                        cur.execute("INSERT INTO peptides(pep_seq) VALUES ('{0}')\
                            ON CONFLICT DO NOTHING RETURNING pep_id;".format(peptide))
                    pid = cur.fetchone()[0]
                    cur.execute("INSERT INTO pep_sn(pep_id, sn_sp) VALUES ('{0}', '{1}')\
                            ON CONFLICT DO NOTHING;".format(pid, species))
                    cur.execute("INSERT INTO pep_pr(pep_id, pr_acc) VALUES ('{0}', '{1}') \
                            ON CONFLICT DO NOTHING;".format(pid, pr))
                except psycopg2.ProgrammingError as e:
                    print("Insert error")
                    print(e)
                    conn.rollback()
                    print("Rollback complete")

                conn.commit()


## Lectins
dirname = "../data/lectins"
directory = os.fsencode(dirname)
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".csv"): 
        continue;
    print("Processing: " + filename)

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        lectin = file.decode("utf-8")[:-4]
        species = ''
        protein = ''
        count = 0
        for row in reader:
            if row['Venom'] != '':
                species = row['Venom'].split()[1]
            if row['Accession number'] != '' and row['Toxin class'] != '':
                protein = row['Accession number']
                toxclass = row['Toxin class']
                for pr in protein.split(','):
                    pr = pr.strip()
                    try:
                        cur.execute("SELECT * FROM proteins WHERE pr_acc = '{0}';".format(pr))
                    except psycopg2.ProgrammingError as e:
                        print(e)
                        conn.rollback()
                        print("Rollback complete")
                    conn.commit()
                    if cur.rowcount == 0:
                        try:
                            cur.execute("INSERT INTO proteins(pr_acc, pr_toxclass, pr_{0}) VALUES ('{1}', '{2}', 1)\
                            ON CONFLICT DO NOTHING;".format(lectin, pr, toxclass))
                            cur.execute("INSERT INTO pr_sn(pr_acc, sn_sp) VALUES ('{0}', '{1}')\
                            ON CONFLICT DO NOTHING;".format(pr, species))
                        except psycopg2.ProgrammingError as e:
                            print("Insert error")
                            print(e)
                            conn.rollback()
                            print("Rollback complete")
                        conn.commit()
                    else: 
                        try:
                            cur.execute("UPDATE proteins SET pr_{0} = 1 WHERE pr_acc = '{1}';".format(lectin, pr))
                        except psycopg2.ProgrammingError as e:
                            print("Insert error")
                            print(e)
                            conn.rollback()
                            print("Rollback complete")
                        conn.commit()

            peptide = row['Peptides'].upper()
            if (peptide == ''): 
                continue;
            for pr in protein.split(','):
                pr = pr.strip()
                try:
                    cur.execute("SELECT pep_id FROM peptides WHERE pep_seq = '{0}';".format(peptide))
                    if (cur.rowcount == 0):
                        cur.execute("INSERT INTO peptides(pep_seq) VALUES ('{0}')\
                            ON CONFLICT DO NOTHING RETURNING pep_id;".format(peptide))
                    pid = cur.fetchone()[0]
                    cur.execute("INSERT INTO pep_sn(pep_id, sn_sp) VALUES ('{0}', '{1}')\
                            ON CONFLICT DO NOTHING;".format(pid, species))
                    cur.execute("INSERT INTO pep_pr(pep_id, pr_acc) VALUES ('{0}', '{1}') \
                            ON CONFLICT DO NOTHING;".format(pid, pr))
                except psycopg2.ProgrammingError as e:
                    print("Insert error")
                    print(e)
                    conn.rollback()
                    print("Rollback complete")
                conn.commit()

cur.close()
conn.close()

