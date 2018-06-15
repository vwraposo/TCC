import sys
sys.path.insert(0, '../src/')
import middleware as mw
import pytest
from Bio.SeqRecord import SeqRecord

def test_answer ():
    records = mw.getAlignedSeq("12S")
    assert len(records) == 7
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
    assert len(records) == 7
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1')
    records = mw._getProteins('L')
    assert len(records) == 7
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1' or i == '2' or i == '3' or i == '4')
    records = mw._getProteins('TL')
    assert len(records) == 7
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1' or i == '2' or i == '3' or i == '4')

def test_getPeptides():
    records = mw._getPeptides()
    assert len(records) == 7
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1')

def test_getGlycans():
    records = mw._getGlycans()
    assert len(records) == 7
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1')

