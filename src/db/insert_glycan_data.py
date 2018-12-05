##################################################################################
##                                                                              ##
##  Module that insert the  N-glycan  data from csv files                       ##
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

filename = "../../data/N-glycans_table.csv"
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

cur.close()
conn.close()

            

