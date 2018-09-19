##################################################################################
##                                                                              ##
##   Module that will work as a middleware for the program that generates       ##
## the NEXUS file to create nexus files regarding the data from B. atrox        ##
##################################################################################
import psycopg2
import sys
import tempfile 
from UF import UnionFind 
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast import NCBIXML

def _getPeptides(typ=''):
    MAX_DIFF = 2
    MAX_HITS = 5
    MIN_SCORE = 20 
    MIN_EVALUE = 1e-05

    try:
        conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    except:
        print("Error: it was not possible to connect to the database")
        sys.exit(1)
    cur = conn.cursor()

    try:

        cur.execute("SELECT DISTINCT pep_id FROM pep_at;")
        if cur.rowcount == 0:
            print("Error: there are not peptides in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    peptides = [tup[0] for tup in cur]
    n_pep = len(peptides)
    dic = dict(zip(peptides, range(n_pep)))
    dicI = dict(zip(range(n_pep), peptides))
    
    uf = UnionFind(n_pep)
    
    out_file = tempfile.NamedTemporaryFile()
    blastp_cline = NcbiblastpCommandline(query="../data/blast/atrox_peptides.faa", db="../data/blast/db/atrox_peptides", evalue=MIN_EVALUE, threshold=MIN_SCORE, max_target_seqs=MAX_HITS, num_threads = 3, outfmt=5, out=out_file.name)
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
        if typ == "R":
            cur.execute("SELECT DISTINCT r.pep_id, at.at_habitat, at.at_replicate \
                    FROM pep_at AS r, atrox AS at \
                    WHERE r.at_id = at.at_id;")
        else:
            cur.execute("SELECT DISTINCT r.pep_id, at.at_habitat \
                    FROM pep_at AS r, atrox AS at \
                    WHERE r.at_id = at.at_id;")
        if cur.rowcount == 0:
            print("Eror: there are not peptides related to species in the database.")
            raise Exception
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

    records = dict()
    for tup in cur: 
        if typ == "R":
            k = "{0}_{1}".format(tup[1], tup[2])
        else:
            k = tup[1]
        if k not in records:
            records[k] = [str(0)] * len(classes)  
        
        f = dicI[uf.find(dic[tup[0]])]
        records[k][classes.index(f)] = str(1) 

    out_file.close()
    cur.close()
    conn.close()

    return records
