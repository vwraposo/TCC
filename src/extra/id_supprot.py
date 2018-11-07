##################################################################################
##                                                                              ##
##  Module that identifies the supporting proteins to the neuwiedi discrepancy  ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import os
import re


def idProteins(report, mn=5):
    directory = "../reports/supp_prot/"
    classes = {}
    with open(directory + "class.txt") as f:
        for line in f:
            line = line.split(':')
            classes[int(line[0])] = int(line[1][:-1])

    peptides = []
    with open(report, 'r') as f:
        f.readline(), f.readline()
        for line in f: 
            peptides.append(classes[int(line.split()[2])])
    
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT r.pr_acc, r.pep_id FROM pep_pr AS r, proteins AS pr  WHERE pr.pr_acc = r.pr_acc AND pr.pr_T = 1 ;")
        if cur.rowcount == 0:
            print("Error: empty query.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    proteins = {} 

    for tup in cur: 
        pr_acc = tup[0]
        pep_id = int(tup[1])
        if pr_acc not in proteins:
            proteins[pr_acc] = 0

        if classes[pep_id] in peptides:
            proteins[pr_acc] += 1

    proteins = list(filter(lambda x: proteins[x] >= mn, proteins.keys()))
    filename = report.split('/')[-1]
    with open(directory + filename, "w") as f:
        f.write("Report with the supporting proteins from the '{0}' report.\n\n".format(filename)) 
        for pr in proteins:
            f.write(pr + '\n')


idProteins('../reports/supp_peptides2/report_9v5.txt')
idProteins('../reports/supp_peptides2/report_10v9.txt')
idProteins('../reports/supp_peptides2/report_2v5.txt')
idProteins('../reports/supp_peptides2/report_6v5.txt')
idProteins('../reports/supp_peptides2/report_9v5.txt')
idProteins('../reports/supp_peptides2/report_9vneuwiedi.txt')




