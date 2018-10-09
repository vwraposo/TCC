##################################################################################
##                                                                              ##
##  Module that identifies the supporting peptides to the neuwiedi discrepancy  ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import os

import re

def similar (x, y):
    eps = 0.05
    s = abs(float(x[1]) - float(y[1])) 
    return (s < eps)

def parse (filename):
    lines = [line.split() for line in open(filename) if re.match(r'^character', line)]
    ret = dict((l[1], (l[2][2:], l[3][2:])) for l in lines)
    return ret

def diff (p, q):
    l = [ch for ch in p if not similar(p[ch], q[ch])]
    return l

directory = "../reports/supp_peptides/"
with open(directory + "char_matrix.txt") as f:
    ids = f.readline().split("\t#")
    ids[0] = ids[0][1:]
    ids[-1] = ids[-1][:-1]

try:
    conn = psycopg2.connect(dbname="testdb",  user="fox", password="senha")
except:
    print("Error: It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()

p = parse("../reports/supp_peptides/10.txt")
q = parse("../reports/supp_peptides/9.txt")

l = diff (p, q)

output = open("../reports/supp_peptides/report.txt", "w")
output.write("Report comparing the nodes 9 and 10 from the tree. The list below is comprised of the peptides that causes the branching between this nodes\n\n")
for i in l:
    try:
        cur.execute("SELECT * FROM peptides WHERE pep_id = {0};".format(ids[int(i)-1]))
    except psycopg2.ProgrammingError as e:
        print("Error")
        print(e)
        conn.rollback()
        print("Rollback complete")
    conn.commit()

    peptide = cur.fetchone()
    output.write("Peptide ID: {0} Sequence: {1}\n".format(peptide[0], peptide[1]))

output.close

cur.close()
conn.close()

