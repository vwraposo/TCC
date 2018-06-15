##################################################################################
##                                                                              ##
##  Module that insert the  N-glycan  data from csv files                       ##
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

filename = "../data/N-glycans_table.csv"
with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        fieldnames = reader.fieldnames
        for row in reader:
            gl_id = row[fieldnames[0]]
            try:
                cur.execute("INSERT INTO glycans(gl_id) VALUES ('{0}');".format(gl_id))
            except psycopg2.ProgrammingError as e:
                print("Insert error")
                print(e)
                conn.rollback()
                print("Rollback complete")

            conn.commit()

            for sp in fieldnames[2:]:
                if row[sp] == '0':
                    continue
                species = sp.split()[1]
                try:
                    cur.execute("INSERT INTO gl_sn(gl_id, sn_sp) VALUES ('{0}', '{1}');"\
                        .format(gl_id, species))
                except psycopg2.ProgrammingError as e:
                    print("Insert error")
                    print(e)
                    conn.rollback()
                    print("Rollback complete")

                conn.commit()

            

