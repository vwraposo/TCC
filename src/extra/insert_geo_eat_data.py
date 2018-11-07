##################################################################################
##                                                                              ##
##  Module that insert geographic and eating habits data from csv files         ##
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

# Geographic data
filename = "../data/geography.csv"
with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            sp = row['Species'].split()[1]
            locs = row['States'].split(',')
            for loc in locs:
                loc = loc.strip()
                try:
                    cur.execute("INSERT INTO geography(sn_sp, loc) VALUES ('{0}', '{1}');".format(sp, loc))
                except psycopg2.ProgrammingError as e:
                    print("Insert error")
                    print(e)
                    conn.rollback()
                    print("Rollback complete")

                conn.commit()
# Eating habits data
filename = "../data/eating.csv"
with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            r = list(row.values())
            r[0] = r[0].split()[1]
            try:
                cur.execute("INSERT INTO eating(sn_sp, N, centipedes, anurans, lizards, snakes, birds, mammals)" \
                        "VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7});".format(*r))
            except psycopg2.ProgrammingError as e:
                print("Insert error")
                print(e)
                conn.rollback()
                print("Rollback complete")

            conn.commit()
cur.close()
conn.close()
