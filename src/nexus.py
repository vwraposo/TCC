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



## Problemas
## - Pode dar override (Talvez nao seja problema)

# TODO:
## - Inserir Mensagens de Erro

class NexusWriter:

    def __init__(self):
        self.dna = collections.OrderedDict() 
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
        for dic in [self.dna, self.standard, self.binary]:
            for c in dic: 
                for k in sorted(dic[c]):
                    m.append(k + ' ' + dic[c][k])
                m.append(" ")
        return '\n'.join(m)

    # Function to convert the format dictionary into string
    def _makeFormat (self):
        f = []
        beg = 1
        end = 0
        dics = [self.dna, self.standard, self.binary]
        names = ['DNA', 'Standard', 'Binary']
        for i in range(len(dics)):
            if len(dics[i]) >= 1:
                for ch in dics[i]:
                    end += self._getSeqLen(ch, dics[i])
                f.append([names[i], beg, end])
                beg = end + 1
        out = []
        if len(f) == 1:
            return f[0][0]
        for it in f:
            out.append(it[0] + ":" + str(it[1]) +'-'+ str(it[2]))
        return "mixed(" + ','.join(out) + ')'
        
    # Function to convert the partition dictionary into string
    def _makePartition (self):
        s = []
        clist = [] 
        beg = 1
        end = 0
        tot = 0
        for dic in [self.dna, self.standard, self.binary]:
            for cset in dic:
                tot += 1
                end += self._getSeqLen(cset, dic) 
                s.append("\tcharset {0} = {1}-{2};".format(cset, beg, end))
                clist.append(cset)
                beg = end + 1

        s.append("\tpartition part = {0}: {1};".format(tot, ", ".join(clist)))
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




                 
