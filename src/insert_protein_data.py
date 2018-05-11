##################################################################################
##                                                                              ##
##  Module that insert the protein and peptide data from xls files              ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import os
import xlrd


try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()
f = '../data/protein/proteins.xls'

wb = xlrd.open_workbook(f)
for sh in wb.sheets()[:-1]:
    species = sh.name[3:]
    print("Processing sheet from: " + species)

    acc = list(filter(lambda x: x.ctype != xlrd.XL_CELL_EMPTY, sh.col(2)))
    toxclass = list(filter(lambda x: x.ctype != xlrd.XL_CELL_EMPTY, sh.col(6)))
    peptides = list(filter(lambda x: x.ctype != xlrd.XL_CELL_EMPTY, sh.col(7)))

    for i in range(1, len(acc)):
        try:
            cur.execute("INSERT INTO proteins(pr_acc, pr_toxclass) VALUES ('{0}', '{1}')\
                    ON CONFLICT DO NOTHING;".format(str(acc[i].value), str(toxclass[i].value)))
            cur.execute("INSERT INTO pr_sn(pr_acc, sn_sp) VALUES ('{0}', '{1}')\
                    ON CONFLICT DO NOTHING;".format(str(acc[i].value), species))
        except psycopg2.ProgrammingError as e:
            print("Insert error")
            print(e)
            conn.rollback()
            print("Rollback complete")

        conn.commit()

    for i in range(1, len(peptides)):
        try:
            cur.execute("INSERT INTO peptides(pep_seq) VALUES ('{0}')\
                    ON CONFLICT DO NOTHING;".format(str(peptides[i].value)))
            cur.execute("INSERT INTO pep_sn(pep_seq, sn_sp) VALUES ('{0}', '{1}')\
                    ON CONFLICT DO NOTHING;".format(str(peptides[i].value), species))
        except psycopg2.ProgrammingError as e:
            print("Insert error")
            print(e)
            conn.rollback()
            print("Rollback complete")

        conn.commit()



cur.close()
conn.close()

