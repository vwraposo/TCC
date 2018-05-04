##################################################################################
##                                                                              ##
##   Module that has a Nexus file writer                                        ##
##                                                                              ##
##################################################################################

from string import Template
import collections

data_template = Template("""#NEXUS

Begin data;
        Dimensions ntax=$ntax nchar=$nchar;
        Format datatype=$datatype interleave=yes gap=- missing=?;
        Matrix
$matrix
    ;
End;
""")

mb_template = Template("""begin mrbayes;
    $partition

    $code

end;
""")



# TODO:
## - Inserir Mensagens de Erro
## - Testes

class NexusWriter:

    def __init__(self):
        self.dna = collections.OrderedDict() 
        self.codon = collections.OrderedDict()
        self.standard = collections.OrderedDict() 
        self.binary = collections.OrderedDict() 
        self.taxa = set()
        self.tchar = 0
        # <charset> : <seq> #

    # Function to add a new data entry, recieves a taxon, the type of data and the sequence. 
    def add (self, taxa, charset, datatype, seq):
        # Updating datastructures
        if datatype == 'DNA':
            dic = self.dna
        elif datatype == 'Codon':
            dic = self.codon
        elif datatype == 'Standard':
            dic = self.standard
        elif datatype == 'Binary':
            dic = self.binary
        else:
            print("Error")

        if charset not in dic:
            self.tchar += len(seq)
            dic[charset] = dict()
        self.taxa.add(taxa)
        dic[charset][taxa] = seq

    # Function that writes the nexus file
    def writeFile (self, outfile):
        data = data_template.substitute(
            ntax = len(self.taxa), 
            nchar = self.tchar, 
            datatype = self._makeFormat(),
            matrix = self._makeMatrix()
                )

        code = mb_template.substitute(
            partition = self._makePartition(), 
            code = self._makeCode()
            )
        f = open(outfile, 'w')
        f.write(data)
        f.write(code)
        f.close()

    # Function to convert the data matrix into string
    def _makeMatrix (self):
        m = []
        for dic in [self.dna, self.codon, self.standard, self.binary]:
            for c in dic: 
                for k in sorted(dic[c]):
                    m.append(k + ' ' + dic[c][k])
                m.append(" ")
        return '\n'.join(m)

    # Function to convert the format dictionary into string
    def _makeFormat (self):
        f = dict()
        beg = 1
        end = 0
        dics = [self.dna, self.codon, self.standard, self.binary]
        names = ['DNA', 'DNA', 'Standard', 'Binary']
        for i in range(len(dics)):
            if len(dics[i]) >= 1:
                for ch in dics[i]:
                    end += self._getSeqLen(ch, dics[i])
                if names[i] not in f:
                    f[names[i]] = [beg, end]
                else :
                    f[names[i]][1] = end 
                beg = end + 1
        out = []
        if len(f) == 1:
            return list(f.items())[0][0]
        for i in f:
            out.append(i + ":" + str(f[i][0]) +'-'+ str(f[i][1]))
        return "mixed(" + ','.join(out) + ')'
        
    # Function to convert the partition dictionary into string
    def _makePartition (self):
        s = []
        clist = [] 
        beg = 1
        end = 0
        for dic in [self.dna, self.codon, self.standard, self.binary]:
            for cset in dic:
                end += self._getSeqLen(cset, dic) 
                if dic == self.codon:
                    s.append("\tcharset {0}_1st = {1}-{2}\\3;".format(cset, beg, end))
                    clist.append(cset + '_1st')
                    s.append("\tcharset {0}_2nd = {1}-{2}\\3;".format(cset, beg+1, end))
                    clist.append(cset + '_2nd')
                    s.append("\tcharset {0}_3rd = {1}-{2}\\3;".format(cset, beg+2, end))
                    clist.append(cset + '_3rd')
                else:
                    s.append("\tcharset {0} = {1}-{2};".format(cset, beg, end))
                    clist.append(cset)
                beg = end + 1

        s.append("\tpartition part = {0}: {1};".format(len(clist), ", ".join(clist)))
        s.append("\tset partition = part;")
        return '\n'.join(s)
    
    # Function to convert the partition dictionary into string
    def _makeCode (self):
        c = []
        if len(self.dna) >= 1:
            c.append("\tlset applyto=({0}) nst=mixed rates=invgamma;".format(",".join(str(x) for x in list(range(1, len(self.dna) +1)))))
        c.append("\tunlink revmat=(all) pinvar=(all) shape=(all) statefreq=(all);")
        c.append("\tprset ratepr=variable;")
        return '\n'.join(c)


    def _getSeqLen(self, charset, dic):
        return len(list(dic[charset].values())[0])




                 