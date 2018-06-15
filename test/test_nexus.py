import sys 
sys.path.insert(0, '../src/')
from nexus import NexusWriter
import pytest

def test_add ():
   n = NexusWriter ()
   n.add ('T1', 'c1', 'DNA', 'AGC')
   n.add ('T2', 'c2', 'DNA', 'AGC')
   n.add ('T1', 'c3', 'Codon', '-GC')
   n.add ('T1', 'c4', 'Standard', '047')
   n.add ('T1', 'c5', 'Binary', '010')
   assert len(n.dna) == 2
   assert len(n.codon) == 1
   assert len(n.standard) == 1
   assert len(n.binary) == 1
   assert len(n.taxa) == 2
   assert n.tchar == 15 


def test_GenParams():
    n = NexusWriter ()
    with pytest.raises(Exception):
        n.setNgen("NOT NUMBER")
        n.setSampleFreq("NOT NUMBER")
    n.setNgen("1")
    n.setSampleFreq("1")
    assert n.ngen == 1
    assert n.smpfreq == 1


def test_addError():
    n = NexusWriter ()
    with pytest.raises(Exception):
        n.add ('T1', 'c1', 'DNA', 'A12345')
    with pytest.raises(Exception):
        n.add ('T1', 'c1', 'Codon', 'A12345')
    with pytest.raises(Exception):
        n.add ('T1', 'c1', 'Standard', '123ABC45')
    with pytest.raises(Exception):
        n.add ('T1', 'c1', 'Binary', '12345')
    with pytest.raises(Exception):
        n.add ('T1', 'c1', 'Binary', 'ADVKLD')

def test_sameLen ():
    n = NexusWriter ()
    n.add ('T1', 'c1', 'DNA', 'AGC')
    with pytest.raises(Exception):
        n.add ('T2', 'c1', 'DNA', 'AGCAA')

def test_makeMatrix ():
    n = NexusWriter ()
    n.add ('T1', 'c1', 'DNA', 'AGC')
    n.add ('T1', 'c2', 'Codon', '?AGC')
    n.add ('T1', 'c3', 'Standard', '047')
    print(n._makeMatrix())
    assert n._makeMatrix() == '\tT1 AGC\n\n\tT1 ?AGC\n\n\tT1 047\n'

def test_makeFormat ():
    n = NexusWriter ()
    n.add ('T1', 'c1', 'DNA', 'AGC')
    n.add ('T1', 'c3', 'Codon', 'AGC')
    assert n._makeFormat() == 'DNA'
    n.add ('T1', 'c4', 'Standard', '047')
    assert n._makeFormat() == 'mixed(DNA:1-6,Standard:7-9)'

def test_makePartition ():
    n = NexusWriter ()
    n.add ('T1', 'c1', 'DNA', 'AGC')
    n.add ('T1', 'c3', 'Codon', 'AGC')
    n.add ('T1', 'p', 'Standard', '01010')
    n._makePartition ()
    assert n._partition['dna'] == ['1']
    assert n._partition['codon'] == ['2', '3', '4']
    assert n._partition['standard'] == ['5']



def test_getSeqLen():
    n = NexusWriter ()
    n.add ('T1', 'c1', 'DNA', 'AGC')
    n.add ('T1', 'c2', 'Standard', '123')
    n.add ('T1', 'c3', 'Standard', '123456')
    assert n._getSeqLen('c1', n.dna) == 3
    assert n._getSeqLen('c3', n.standard) == 6

