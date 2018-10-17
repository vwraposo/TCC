##################################################################################
##                                                                              ##
##   Module that workds as a middleware for the program that generates          ##
## the NEXUS file, meaning when the user asks for a type of data the program    ##
## call this module to get the aligned sequences that will go to the NEXUS file ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import tempfile 
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna, generic_protein
from Bio.Align.Applications import ClustalOmegaCommandline
from pep_equiv import PepEquiv

# Recieve a type (alias) of gene, then get the sequences from the database and returns the aligned sequences  
def getAlignedSeq(alias):
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM genes WHERE gn_alias = '{0}';".format(alias))
        if cur.rowcount == 0:
            print("Eror: no data with the alias: {0}".format(alias))
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")


    records = []
    for tup in cur:
        records.append(SeqRecord(Seq(tup[2], generic_dna), id=tup[0], name=tup[4], description=tup[1]))

    in_file = tempfile.NamedTemporaryFile()
    out_file = tempfile.NamedTemporaryFile()

    SeqIO.write(records, in_file.name, "fasta")

    clustalomega_cline = ClustalOmegaCommandline(infile=in_file.name, outfile=out_file.name, verbose=True, auto=True, force=True)
    clustalomega_cline()

    records = []
    for record in SeqIO.parse(out_file.name, "fasta"):
        record.seq.alphabet = generic_dna
        records.append(record)

    in_file.close()
    out_file.close()
    cur.close()
    conn.close()

    return records


def getStandard(chset):
    if chset == 'protein':
        return _getProteins('T')
    elif chset == 'lec_protein':
        return _getProteins('L') 
    elif chset == 'all_protein':
        return _getProteins('TL') 
    elif chset == 'peptides':
        return _getPeptides('T')
    elif chset == 'all_peptides':
        return _getPeptides()
    elif chset == 'glycans':
        return _getGlycans()
    else:
        print("Error: charset not defined.")
        raise Exception

# Returns the proteic data from the database in a standard form 
def _getProteins(typ):
    if typ == 'T':
        where = 'WHERE pr.pr_acc = r.pr_acc AND pr.pr_T = 1' 
    elif typ == 'L':
        where = 'WHERE pr.pr_acc = r.pr_acc AND (pr.pr_WGA = 1 OR pr.pr_ConA = 1 OR pr.pr_PNA = 1)'
    elif typ == 'TL':
        where = ''
    else:
        print("Error: protein type not defined.")
        raise Exception

    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT r.pr_acc FROM pr_sn AS r, proteins AS pr {0};".format(where))
        if cur.rowcount == 0:
            print("Error: there are not proteins in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    proteins = [tup[0] for tup in cur]

    if typ == 'T':
        where = 'AND pr_T = 1' 
    elif typ == 'L':
        where = 'AND (pr_WGA = 1 OR pr_ConA = 1 OR pr_PNA = 1)'
    elif typ == 'TL':
        where = ''


    try:
        cur.execute("SELECT DISTINCT * FROM pr_sn, proteins WHERE pr_sn.pr_acc = proteins.pr_acc {0};".format(where))
        if cur.rowcount == 0:
            print("Eror: there are not proteins related to species in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if tup[0] not in records:
            records[tup[0]] = [str(0)] * len(proteins)  

        summ = 1
        if typ == 'L' or typ == 'TL':
            summ = sum(tup[4:])
        records[tup[0]][proteins.index(tup[1])] = str(summ)

    cur.close()
    conn.close()
    return records

# Returns the proteic data from the database in a binary form 
def _getPeptides(typ=''):

    if typ == "T":
        where =  "WHERE pep_id IN (SELECT DISTINCT pe.pep_id \
                    FROM pep_pr AS pe, proteins AS pr \
                    WHERE pe.pr_acc = pr.pr_acc AND pr.pr_T = 1)"
        db = "peptides"
    else:
        where = ""
        db = "all_peptides"

    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)
    cur = conn.cursor()

    try:

        cur.execute("SELECT DISTINCT pep_id FROM pep_sn {0};".format(where))
        if cur.rowcount == 0:
            print("Error: there are not peptides in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    peptides = [tup[0] for tup in cur]

    equiv = PepEquiv(peptides, db)

   
    classes = equiv.getClasses()

    try:
        cur.execute("SELECT DISTINCT * FROM pep_sn {0};".format(where))
        if cur.rowcount == 0:
            print("Eror: there are not peptides related to species in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if tup[1] not in records:
            records[tup[1]] = [str(0)] * len(classes)  
        
        f = equiv.getRep(tup[0])
        records[tup[1]][classes.index(f)] = str(1) 

    ## Creating a file with the id of the class representative
    # with  open("character_file.nex", "a") as f:
        # f.write("{0};\n".format(len(classes)))
        # f.write("CHARSTATELABELS\n")
        # for i in range(len(classes)-1):
            # f.write("{0} {1}, ".format(str(i+1), classes[i]))
        # f.write("{0} {1} ;\n".format(str(len(classes)), classes[-1]))
        # f.write("MATRIX\n")
        # for sn in records:
            # f.write("{0} {1}\n".format(str(sn), ''.join(records[sn])))
        # f.write(";\nEND;")

    cur.close()
    conn.close()

    return records

# Returns the N-glycan data from the database in a binary form 
def _getGlycans():
    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT gl_id FROM gl_sn;")
        if cur.rowcount == 0:
            print("Error: there are not glycans in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    glycans = [tup[0] for tup in cur]
    try:
        cur.execute("SELECT DISTINCT * FROM gl_sn;")
        if cur.rowcount == 0:
            print("Eror: there are not glycans related to species in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if tup[1] not in records:
            records[tup[1]] = [str(0)] * len(glycans)  

        records[tup[1]][glycans.index(tup[0])] = str(1)

    cur.close()
    conn.close()
    

    return records
