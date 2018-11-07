import sys
sys.path.insert(0, '../src/')
import middleware as mw
import pytest
from Bio.SeqRecord import SeqRecord

def test_answer ():
    records = mw.getAlignedSeq("12S")
    for rec in records:
        assert isinstance(rec, SeqRecord)

def test_error ():
    with pytest.raises(Exception):
        mw.getAlignedSeq("S")

def test_getProteinError():
    with pytest.raises(Exception):
        mw._getProteins('NotDef')

def test_getProteins():
    records = mw._getProteins('T')
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1')
    records = mw._getProteins('L')
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1' or i == '2' or i == '3' or i == '4')
    records = mw._getProteins('TL')
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1' or i == '2' or i == '3' or i == '4')

def test_getPeptides():
    records = mw._getPeptides('T')
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1')
            
    records = mw._getPeptides('TL')
     for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1' or i == '2' or i == '3' 

def test_getGlycans():
    records = mw._getGlycans()
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1')

