##################################################################################
##                                                                              ##
##   Module that lets a user choose the data from the database and then         ##
##   builds a nexus file that will be the input for MrBayes.                    ##
##                                                                              ##
##################################################################################
import align as al
from nexus import NexusWriter
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_dna
import cmd
import psycopg2


class CreateInput(cmd.Cmd):

    def __init__ (self):
        super(CreateInput, self).__init__()
        self.nwriter = NexusWriter()
        self.charset = dict()
        self.selected = dict()
        ## Setup
        try:
            conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
        except:
            print("Error: it was not possible to connect to the database")
            sys.exit(1)

        cur = conn.cursor()
        self.charset['mtDNA'] = []
        try:
            cur.execute("SELECT DISTINCT mt_alias FROM mtdnas;")
            for ch in cur:
                self.charset['mtDNA'].append(ch[0])
                self.selected[ch[0]] = False
        except psycopg2.ProgrammingError as e:
            print(e)
            conn.rollback()
            print("Rollback complete")
        
        cur.close()
        conn.close()
        self.do_list("")
    
    def emptyline(self):
         pass

    def add(self, chset, datatype):
        # Recieves a charset and add to the Writer 
        try:
            records = al.getAlignedSeq(chset) 
            self.selected[chset] = datatype
        except:
            return
        for rec in records:
            try:
                self.nwriter.add(rec.description.split()[2], chset, datatype, str(rec.seq))
            except:
                break

    #TODO: def add_all(self, datatype):

    def do_add_codon(self, arg):
        if len(arg.split()) != 1:
            print("Error:")
        else:
            self.add(arg, 'Codon')
    def do_add_std(self, arg):
        if len(arg.split()) != 1:
            print("Error:")
        else:
            self.add(arg, 'Standard')
    def do_add_bin(self, arg):
        if len(arg.split()) != 1:
            print("Error:")
        else:
            self.add(arg, 'Binary')
    def do_add_dna(self, arg):
        if len(arg.split()) != 1:
            print("Error:")
        else:
            self.add(arg, 'DNA')

    def do_write (self, arg):
        self.nwriter.writeFile(arg)
        print ("Writing NEXUS file: " + arg)

    def do_list(self, args):
        out = []
        s = ""
        out.append('-' * (17 * len(self.charset)))
        for typ in self.charset:
            s = s + " {0}{1}|".format(typ, " "* (15 - len(typ)))
        out.append(s)
        out.append('-' * (17 * len(self.charset)))
        ## ARRUMAR QUANDO TIVER MAIS TIPO DE DADO 
        for ch in self.charset['mtDNA']:
            tmp = ""
            if self.selected[ch] != False:
                tmp = "* ({0})".format(self.selected[ch])
            out.append(" {0} {1}{2}|".format(ch, tmp, " " * (15 - len(ch) - len(tmp) -1)))
        out.append('-' * (17 * len(self.charset)))
        out.append('* (<datatype>) - charset was selected as <datatype>')
        print('\n'.join(out))

    def do_quit(self, args):
        # Quits the program
        print("Quitting.")
        raise SystemExit


if __name__ == '__main__':
    prompt = CreateInput()
    prompt.prompt = '> '
    prompt.cmdloop('\nProgram to create NEXUS files for MrBayes from the database.\nWrite "help" for commands.\n' \
            "All data is shown above. You can add it to the NEXUS file by using the commands:\n\tadd_<datatype> <charset>\n")
    # records = al.getAlignedSeq('16S') 
# n = NexusWriter()
# for rec in records:
    # n.add(rec.description.split()[2], '16S', 'DNA', str(rec.seq))
# records = al.getAlignedSeq('ND4') 
# for rec in records:
    # n.add(rec.description.split()[2], 'ND4', 'Codon', str(rec.seq))
# records = al.getAlignedSeq('12S') 
# for rec in records:
    # n.add(rec.description.split()[2], '12S', 'DNA', str(rec.seq))
# records = al.getAlignedSeq('cytb') 
# for rec in records:
    # n.add(rec.description.split()[2], 'cytb', 'Codon', str(rec.seq))
# n.writeFile("../input/molecular.nex")


