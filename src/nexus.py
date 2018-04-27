##################################################################################
##                                                                              ##
##   Module that has a Nexus file writer                                        ##
##                                                                              ##
##################################################################################

from string import Template
template = Template("""#NEXUS

Begin data;
        Dimensions ntax=$ntax nchar=$nchar;
        Format datatype=$datatype interleave=yes gap=- missing=?;
        Matrix
$matrix
    ;
End;
""")


## Problemas
## - So permite receber agrupado por tipo, nao pode recever DNA, Standard e DNA (sera que e problema? Daria para usar uma lista e checar a ultima entrada
## - Pode dar override (Talvez nao seja problema)

class NexusWriter:

    def __init__(self):
        self.taxa = set()
        self.data = dict()
        self._nchar = 1
        self._format = dict()

    # Function to add a new data entry, recieves a taxon, the type of data and the sequence. 
    def add (self, taxa, typ, datatype, seq):
        # Updating datastructures
        self.taxa.add(taxa)
        if typ not in self.data:
            if datatype not in self._format:
                self._format[datatype] = [str(self._nchar), ""]
            self._nchar += len(seq)
            self._format[datatype][1] = str(self._nchar)
            self.data[typ] = dict()

        self.data[typ][taxa] = seq



    # Function that writes the nexus file
    def writeFile (self, outfile):
        s = template.substitute(
            ntax = len(self.taxa), 
            nchar = self._nchar, 
            datatype = self._makeFormat(),
            matrix = self._makeMatrix()
                )
        f = open(outfile, 'w')
        f.write(s)
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
        
