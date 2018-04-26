import psycopg2
import sys
import os

try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Nao foi possivel conectar ao banco de dados")
    sys.exit(1)

cur = conn.cursor()

dirname = "../data/mtDNA"
directory = os.fsencode(dirname)
for file in os.listdir(directory):
    filename = dirname + "/" + os.fsdecode(file)
    if not filename.endswith(".txt"): 
        continue;
    print ("Arquivo sendo processsado: " +  filename);
    data = open(filename, 'r')
    with open(filename, 'r') as f:
        for line in f:
            line = line[:-1]
            line = line.split("#");
            mt_acc = line[0] 
            mt_desc = line[1] 
            mt_alias = line[2] 
            mt_seq = line[3] 
            sn_sp = mt_desc.split()[1]

            try:
                cur.execute("INSERT INTO mtDNAs(mt_acc, mt_desc, mt_seq, mt_alias, sn_sp) VALUES"
                    "('{0}', '{1}', '{2}', '{3}', '{4}');".format(mt_acc, mt_desc, mt_seq, mt_alias, sn_sp))
            except psycopg2.ProgrammingError as e:
                print("Erro no insert")
                print(e)
                conn.rollback()
                print("Rollback concluido")

            conn.commit()
            data.close()

cur.close()
conn.close()
