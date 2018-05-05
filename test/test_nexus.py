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
    assert n._makeMatrix() == 'T1 AGC\n\nT1 ?AGC\n\nT1 047\n'

def test_makeFormat ():
    n = NexusWriter ()
    n.add ('T1', 'c1', 'DNA', 'AGC')
    n.add ('T1', 'c3', 'Codon', 'AGC')
    assert n._makeFormat() == 'DNA'
    n.add ('T1', 'c4', 'Standard', '047')
    assert n._makeFormat() == 'mixed(DNA:1-6,Standard:7-9)'

def test_getSeqLen():
    n = NexusWriter ()
    n.add ('T1', 'c1', 'DNA', 'AGC')
    n.add ('T1', 'c2', 'Standard', '123')
    n.add ('T1', 'c3', 'Standard', '123456')
    assert n._getSeqLen('c1', n.dna) == 3
    assert n._getSeqLen('c3', n.standard) == 6

