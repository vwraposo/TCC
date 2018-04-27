##################################################################################
##                                                                              ##
##   Module that has a Nexus file writer                                        ##
##                                                                              ##
##################################################################################

from string import Template

data_template = Template("""#NEXUS

Begin data;
        Dimensions ntax=$ntax nchar=$nchar;
        Format datacharsete=$datatype interleave=yes gap=- missing=?;
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
## - So permite receber agrupado por tipo, nao pode recever DNA, Standard e DNA (sera que e problema? Daria para usar uma lista e checar a ultima entrada
## - Pode dar override (Talvez nao seja problema)

# TODO:
## - Fazer um format com classe
## - partition dicionario datatype para partititons

class NexusWriter:

    def __init__(self):
        self.taxa = set()
        self.data = dict()
        self._nchar = 1
        self._format = dict() # { <datatype> : [<begin>, <end>] }
        self._partition = dict() # { <charset> : [<begin>, <end>, <datatype>] }

    # Function to add a new data entry, recieves a taxon, the type of data and the sequence. 
    def add (self, taxa, charset, datatype, seq):
        # Updating datastructures
        self.taxa.add(taxa)
        if charset not in self.data:
            self._partition[charset] = [str(self._nchar), "", datatype]
            self.data[charset] = dict()
            if datatype not in self._format:
                self._format[datatype] = [str(self._nchar), ""]

            self._nchar += len(seq)
            self._format[datatype][1] = str(self._nchar - 1)
            self._partition[charset][1] = str(self._nchar - 1)

        self.data[charset][taxa] = seq


    # Function that writes the nexus file
    def writeFile (self, outfile):
        data = data_template.substitute(
            ntax = len(self.taxa), 
            nchar = self._nchar, 
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
        for t in self.data:
            for taxa in self.data[t]:
                m.append(taxa + ' ' + self.data[t][taxa])
            m.append(" ")
        return '\n'.join(m)

    # Function to convert the format dictionary into string
    def _makeFormat (self):
        if len(self._format) == 1:
            return list(self._format)[0];
        out = []
        for it in self._format.items():
            out.append(it[0] + ":" + '-'.join(it[1]))
        return "mixed(" + ','.join(out) + ')'
        
    # Function to convert the partition dictionary into string
    def _makePartition (self):
        s = []
        for cset in self._partition.items():
            s.append("\tcharset {0} = {1};".format(cset[0], '-'.join(cset[1])))
        s.append("\tpartition part = {0}: {1};".format(str(len(self._partition)), " ".join(list(self._partition.keys()))))
        s.append("\tset partition = part;")
        return '\n'.join(s)
    
    # Function to convert the partition dictionary into string
    def _makeCode (self):
        c = []
        part = dict()
        for d in self._format:
            part[d] = []
        i = 1
        for cset in self._partition.items():
            # Garante ordem certa??
            part[cset[1][2]].append(i)
            i+= 1
        if 'DNA' in part:
            c.append("\tlset applyto=({0}) nst=mixed rates=invgamma;".format(",".join(str(x) for x in part['DNA'])))
        c.append("\tunlink revmat=(all) pinvar=(all) shape=(all) statefreq=(all);")
        c.append("\tprset ratepr=variable;")
        return '\n'.join(c)



                 
