##################################################################################
##                                                                              ##
##  Module that insert the peptide data of B.atrox from csv files               ##
##                                                                              ##
##   This file is part of the featsel program                                   ##
##   Copyright (C) 2018 Victor Wichmann Raposo                                  ##
##                                                                              ##
##   This program is free software: you can redistribute it and/or modify       ##
##   it under the terms of the GNU General Public License as published by       ##
##   the Free Software Foundation, either version 3 of the License, or          ##
##   (at your option) any later version.                                        ##
##                                                                              ##
##   This program is distributed in the hope that it will be useful,            ##
##   but WITHOUT ANY WARRANTY; without even the implied warranty of             ##
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              ##
##   GNU General Public License for more details.                               ##
##                                                                              ##
##   You should have received a copy of the GNU General Public License          ##
##   along with this program.  If not, see <http://www.gnu.org/licenses/>.      ##
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

dirname = "../data/atrox_pep/"
directory = os.fsencode(dirname)
l = len(os.listdir(directory))
species = 'atrox'

for file, i in zip(os.listdir(directory), range(l)):
    filename = dirname + os.fsdecode(file)
    if not filename.endswith(".csv"): 
        continue;
    print('Processing: ' + str(i+1) + '/' + str(l))
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            sample = row['Sample name']
            peptide = row['Peptide sequence'].strip()
            if (peptide == '') or (sample == ''):
                continue
            sample = sample.split('_')
            habitat = sample[0]
            replicate = int(sample[2])

            # print(habitat + " " + str(replicate) + " " + peptide)
            try:
                cur.execute("SELECT pep_id FROM peptides WHERE pep_seq = '{0}';".format(peptide))
                if (cur.rowcount == 0):
                    cur.execute("INSERT INTO peptides(pep_seq) VALUES ('{0}')\
                            ON CONFLICT DO NOTHING RETURNING pep_id;".format(peptide))
                pid = cur.fetchone()[0]

                cur.execute("SELECT at_id FROM atrox WHERE at_habitat = '{0}' AND at_replicate = {1};".format(habitat, replicate))
                if (cur.rowcount == 0):
                    cur.execute("INSERT INTO atrox(at_habitat, at_replicate) VALUES ('{0}', {1});".format(habitat, replicate))
                at_id = cur.fetchone()[0]
                cur.execute("INSERT INTO pep_at(pep_id, at_id) VALUES ('{0}', '{1}')\
                        ON CONFLICT DO NOTHING;".format(pid, at_id))
            except psycopg2.ProgrammingError as e:
                print("Insert error")
                print(e)
                conn.rollback()
                print("Rollback complete")

            conn.commit()

cur.close()
conn.close()
