#!/usr/bin/env python3

##################################################################################
##                                                                              ##
##   Module that lets a user choose the data from the database and then         ##
##   builds a nexus file that will be the input for MrBayes.                    ##
##                                                                              ##
##################################################################################

import middleware as mw
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

        ## genes 
        self.charset['genomic'] = []
        try:
            cur.execute("SELECT DISTINCT gn_alias FROM genes;")
            for ch in cur:
                self.charset['genomic'].append(ch[0])
                self.selected[ch[0]] = False
        except psycopg2.ProgrammingError as e:
            print(e)
            conn.rollback()
            print("Rollback complete")
        
        cur.close()
        conn.close()

        ## Standard
        self.charset['Standard'] = ['protein', 'lec_protein', 'all_protein', 'peptides', 'glycans']
        self.selected['protein'] = False 
        self.selected['lec_protein'] = False 
        self.selected['all_protein'] = False 
        self.selected['peptides'] = False 
        self.selected['glycans'] = False

        self.do_list("")
    
    def emptyline(self):
         pass

    # Adds a charset of the given datatype to the nexus file
    def add(self, chset, datatype):
        if (chset in self.selected and self.selected[chset] != False):
            print("Error: charset '{0}' already selected".format(chset))
            return
        # Recieves a charset and add to the Writer 
        try:
            if datatype == 'DNA' or datatype == 'Codon':
                records = mw.getAlignedSeq(chset) 
            elif datatype == 'Standard':
                records = mw.getStandard(chset) 
            self.selected[chset] = datatype
        except:
            return
        for rec in records:
            try:
                if datatype == 'DNA' or datatype == 'Codon':
                    self.nwriter.add(rec.description.split()[2], chset, datatype, str(rec.seq))
                else:
                    self.nwriter.add(rec, chset, datatype, "".join(records[rec]))
            except:
                self.selected[chset] = False
                return
        print("Success: charset '{0}' added".format(chset))


    # Creates a new nwriter
    def do_new (self, args):
        self.nwriter = NexusWriter()
        for i in self.selected:
            self.selected[i] = False
        print("Ready to create a new file.")

    def do_setNgen (self, arg):
        try:
            self.nwriter.setNgen (arg) 
        except:
            return
        print("Success: Number of generations set to {0}.".format(arg))
        
    def do_setSampleFreq (self, arg):
        try:
            self.nwriter.setSampleFreq (arg)
        except:
            return
        print("Success: Sample frequency set to {0}.".format(arg))
    
    # Adds all charsets from the given table to the nexus file
    def do_add_all(self, args):
        for arg in args.split(): 
            if arg not in self.charset:
                print("Error: table '{0}' not in the database".format(arg))
                continue
            if arg == 'genomic':
                datatype = 'DNA'
            else:
                datatype = 'Standard'
            for chset in self.charset[arg]: 
                if self.selected[chset] != False:
                    continue
                if datatype == 'DNA':
                    records = mw.getAlignedSeq(chset) 
                else:
                    records = mw.getStandard(chset) 
                self.selected[chset] = datatype
                error = 0
                for rec in records:
                    try:
                        if datatype == 'DNA':
                            self.nwriter.add(rec.description.split()[2], chset, datatype, str(rec.seq))
                        else:
                            self.nwriter.add(rec, chset, datatype, "".join(records[rec]))
                    except:
                        error = 1
                        break

                if not error:
                    print("Success: charset '{0}' added".format(chset))
                else:
                    print("Error: there was a probles while adding charset '{0}'".format(chset))



    def do_add_codon(self, args):
        for arg in args.split():
            self.add(arg, 'Codon')

    def do_add_std(self, args):
        for arg in args.split():
            self.add(arg, 'Standard')

    def do_add_dna(self, args):
        for arg in args.split():
            self.add(arg, 'DNA')

    def do_write (self, arg):
        try:
            self.nwriter.writeFile(arg)
            print ("Writing NEXUS file: " + arg)
        except Exception as e:
            print(e)
            

    def do_list(self, args):
        out = []
        s = ""
        out.append('-' * (17 * len(self.charset)))
        for typ in self.charset:
            s = s + " {0}{1}|".format(typ, " "* (15 - len(typ)))
        out.append(s)
        out.append('-' * (17 * len(self.charset)))
        for ch in self.charset['genomic']:
            tmp = ""
            if self.selected[ch] != False:
                tmp = "* ({0})".format(self.selected[ch])
            out.append(" {0} {1}{2}|".format(ch, tmp, " " * (15 - len(ch) - len(tmp) -1)))
        for ch in self.charset['Standard']:
            tmp = ""
            if self.selected[ch] != False:
                tmp = "*"
            if (self.charset['Standard'].index(ch) + 3 > len(out) - 1):
                out.append(" {0}|".format(" " * 15) + " {0} {1}{2}|".format(ch, tmp, " " * (15 - len(ch) - len(tmp) -1)))

            else:
                out[self.charset['Standard'].index(ch) + 3] += " {0} {1}{2}|".format(ch, tmp, " " * (15 - len(ch) - len(tmp) -1))
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
