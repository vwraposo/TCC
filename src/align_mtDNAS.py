##################################################################################
##                                                                              ##
##  Module that will have functions that recieve a type of mtDNA, get sequences ##
## from the DB and return all data aligned.                                     ##         
##  It will work as a middleware for the program that generates the NEXUS file, ##
## meaning when the user asks for a type of data the program will use this      ##
## module to get the aligned sequences that will go to the NEXUS file           ##
##                                                                              ##
##################################################################################
import psycopg2
from Bio.Align.Applications import ClustalOmegaCommandline
from subprocess import call

def getAlignedSeq ():
    # try:
        # conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
    # except:
        # print("Nao foi possivel conectar ao banco de dados")
        # sys.exit(1)

    # cur = conn.cursor()
    # Fluxo: Construir arquivo fasta a apartir do DB, chamr clustalo, deletar arquivos FASTA
    in_file = "unaligned.fasta"
    out_file = "aligned.fasta"
    clustalomega_cline = ClustalOmegaCommandline(infile=in_file, outfile=out_file, verbose=True, auto=True)
    clustalomega_cline()

getAlignedSeq ()

