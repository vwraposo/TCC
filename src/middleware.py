##################################################################################
##                                                                              ##
##   Module that will work as a middleware for the program that generates       ##
## the NEXUS file, meaning when the user asks for a type of data the program    ##
## call this module to get the aligned sequences that will go to the NEXUS file ##
##                                                                              ##
##################################################################################
import psycopg2
import sys
import tempfile 
from UF import UnionFind 
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna, generic_protein
from Bio.Align.Applications import ClustalOmegaCommandline
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast import NCBIXML


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
    MAX_DIFF = 2
    MAX_HITS = 5
    MIN_SCORE = 20 
    MIN_EVALUE = 1e-05

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
    n_pep = len(peptides)

    # pep_id -> uf_id
    dic = dict(zip(peptides, range(n_pep)))

    # uf_id -> pep_id
    dicI = dict(zip(range(n_pep), peptides))
    
    uf = UnionFind(n_pep)
    
    out_file = tempfile.NamedTemporaryFile()
    blastp_cline = NcbiblastpCommandline(query="../data/blast/{0}.faa".format(db), db="../data/blast/db/{0}".format(db), evalue=MIN_EVALUE, threshold=MIN_SCORE, max_target_seqs=MAX_HITS, num_threads = 3, outfmt=5, out=out_file.name)
    print("BLAST started....")
    blastp_cline()
    print("BLAST completed.")


    result_handle = open(out_file.name)
    blast_records = NCBIXML. parse(result_handle)
    for blast_record in blast_records:
        pid_t = int(blast_record.query)
        len_t = blast_record.query_letters
        for al in blast_record.alignments:
            pid_r = int(al.title.split()[-1])
            len_r = al.length
            if abs(len_t - len_r) <= MAX_DIFF and pid_t != pid_r:
                if (pid_t not in dic): 
                    print("Error: BLAST database not congruent with local database")
                    sys.exit(1)
                if (pid_r in dic):
                    uf.union (dic[pid_t], dic[pid_r])
                break


    classes  = list(filter(lambda x: dic[x] == uf.find(dic[x]), peptides))


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
        
        f = dicI[uf.find(dic[tup[0]])]
        records[tup[1]][classes.index(f)] = str(1) 

    ## Creating a file with the id of the class representative
    with  open("character_file.nex", "a") as f:
        f.write("{0};\n".format(len(classes)))
        f.write("CHARSTATELABELS\n")
        for i in range(len(classes)-1):
            f.write("{0} {1} / absent present, ".format(str(i+1), classes[i]))
        f.write("{0} {1} / absent present ;\n".format(str(len(classes)), classes[-1]))
        f.write("MATRIX\n")
        for sn in records:
            f.write("{0} {1}\n".format(str(sn), ''.join(records[sn])))
        f.write(";\nEND;")

    out_file.close()
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


_getPeptides()
