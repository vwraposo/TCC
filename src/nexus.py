##################################################################################
##                                                                              ##
##   Module that has a NEXUS file writer                                        ##
##                                                                              ##
##   This file is part of the featsel program                                   ##
##   Copyright (C) 2018 Victor Wichmann Raposo                                  ##
##                                                                              ##
##   This program is free software: you can redistribute it and/or modify       ##
##   it under the terms of the GNU General Public License as published by       ##
##   the Free Software Foundation, either version 3 of the License, or          ##
##   (at your option) any later version.                                        ##
##                                                                              ##
##   This program is distributed in the hope that it will be useful,            ##
##   but WITHOUT ANY WARRANTY; without even the implied warranty of             ##
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              ##
##   GNU General Public License for more details.                               ##
##                                                                              ##
##   You should have received a copy of the GNU General Public License          ##
##   along with this program.  If not, see <http://www.gnu.org/licenses/>.      ##
##                                                                              ##
##################################################################################

from string import Template
import collections
import sys
import re

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

        set partition = part;

    $code

        unlink revmat=(all) pinvar=(all) shape=(all) statefreq=(all);
        prset applyto=(all) ratepr=variable;
        mcmc ngen=$ngen samplefreq=$smpfreq;

end;
""")



class NexusWriter:

    def __init__(self):
        self.dna = collections.OrderedDict() 
        self.codon = collections.OrderedDict()
        self.standard = collections.OrderedDict() 
        self._partition = dict()
        self.taxa = set()
        self.tchar = 0
        # <charset> : <seq> #
        self.ngen = int(2e6)
        self.smpfreq = 100

    # Function to add a new data entry, recieves a taxon, the type of data and the sequence. 
    def add (self, taxon, charset, datatype, seq):
        # Updating datastructures
        self._checkSeq(seq, datatype)
        if datatype == 'DNA':
            dic = self.dna
        elif datatype == 'Codon':
            dic = self.codon
        elif datatype == 'Standard':
            dic = self.standard
        else:
            print("Error: datatype not defined")
            raise(Exception)

        if charset not in dic:
            self.tchar += len(seq)
            dic[charset] = dict()
        self.taxa.add(taxon)
        
        if (len(list(dic[charset].values())) > 0 and len(seq) != len(list(dic[charset].values())[0])):
            print("Error: sequence of same charset with different lengths")
            raise(Exception)
        dic[charset][taxon] = seq


    # Function to set genertion parameters
    def setNgen (self, ngen):
        if not ngen.isdigit():
            print("Parameter is not a number.")
            raise(Exception)
        self.ngen = int(ngen)
    def setSampleFreq (self, smpfreq):
        if not smpfreq.isdigit():
            print("Parameter is not a number.")
            raise(Exception)
        self.smpfreq = int(smpfreq)

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
            code = self._makeCode(), 
            ngen = self.ngen, 
            smpfreq = self.smpfreq
            )
        f = open(outfile, 'w')
        f.write(data)
        f.write(code)
        f.close()

    # Function to convert the data matrix into string
    def _makeMatrix (self):
        m = []
        for dic in [self.dna, self.codon, self.standard]:
            for c in dic: 
                for taxon in sorted(dic[c]):
                    m.append('\t' + taxon + ' ' + dic[c][taxon])
                m.append("")
        return '\n'.join(m)

    # Function to convert the format dictionary into string
    def _makeFormat (self):
        f = dict()
        beg = 1
        end = 0
        dics = [self.dna, self.codon, self.standard]
        names = ['DNA', 'DNA', 'Standard']
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
        p_id = 1
        for dic, name in zip([self.dna, self.codon, self.standard], ['dna', 'codon', 'standard']):
            self._partition[name] = []
            for cset in dic:
                end += self._getSeqLen(cset, dic) 
                if dic == self.codon:
                    s.append("\tcharset {0}_1st = {1}-{2}\\3;".format(cset, beg, end))
                    clist.append(cset + '_1st')
                    self._partition[name].append(str(p_id))
                    p_id += 1
                    s.append("\tcharset {0}_2nd = {1}-{2}\\3;".format(cset, beg+1, end))
                    clist.append(cset + '_2nd')
                    self._partition[name].append(str(p_id))
                    p_id += 1
                    s.append("\tcharset {0}_3rd = {1}-{2}\\3;".format(cset, beg+2, end))
                    clist.append(cset + '_3rd')
                    self._partition[name].append(str(p_id))
                    p_id += 1
                else:
                    s.append("\tcharset {0} = {1}-{2};".format(cset, beg, end))
                    clist.append(cset)
                    self._partition[name].append(str(p_id))
                    p_id += 1
                beg = end + 1

        s.append("\tpartition part = {0}: {1};".format(len(clist), ", ".join(clist)))
        return '\n'.join(s)
    
    # Function to convert the partition dictionary into string
    def _makeCode (self):
        c = []
        if len(self.dna) >= 1:
            c.append("\tlset applyto=({0}) nst=mixed rates=invgamma;".format(','.join(self._partition['dna'])))

        if len(self.codon) >= 1:
            c.append("\tlset applyto=({0}) nst=mixed rates=invgamma;".format(','.join(self._partition['codon'])))

        if len(self.standard) >= 1: 
            c.append("\tlset applyto=({0}) rates=gamma;".format(','.join(self._partition['standard'])))

        return '\n'.join(c)


    def _getSeqLen(self, charset, dic):
        return len(list(dic[charset].values())[0])

    def _checkSeq (self, seq, datatype):
        if (datatype == 'DNA' or datatype == 'Codon'): 
            if (re.match('^[ACGTRYMKSWHBVDN?\-]+$', seq) == None):
                print("Error: sequence {0}... is not in accordance with datatype {1}".format(seq, datatype))
                raise Exception
        elif datatype == 'Standard':
            if not seq.isdigit():
                print("Error: sequence {0}... is not in accordance with datatype {1}".format(seq[:5], datatype))
                raise Exception
        elif datatype == 'Binary':
            for s in seq:
                if (s != '0' and s != '1'):
                    print("Error: sequence {0}... is not in accordance with datatype {1}".format(seq[:5], datatype))
                    raise Exception
        else:
            print("Error: datatype not defined")
            raise Exception


        return


