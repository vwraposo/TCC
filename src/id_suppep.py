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

def create_report(file1, file2):
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


    p = parse(directory + file1)
    q = parse(directory + file2)

    l = diff (p, q)

    output = open("../reports/supp_peptides/report_{0}v{1}.txt".format(file1[:-4], file2[:-4]), "w")
    output.write("Report comparing the nodes {0} and {1} from the tree. The list below is comprised of the peptides that causes the branching between this nodes\n\n".format(file1[:-4], file2[:-4]))
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
        output.write("Peptide ID: {0} \t Sequence: {1}\n".format(peptide[0], peptide[1]))

    output.close

    cur.close()
    conn.close()

create_report("9.txt", "neuwiedi.txt")
create_report("10.txt", "9.txt")
create_report("9.txt", "5.txt")
create_report("6.txt", "5.txt")
create_report("2.txt", "5.txt")


