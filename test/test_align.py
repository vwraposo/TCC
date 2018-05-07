import sys
sys.path.insert(0, '../src/')
import align
import pytest
from Bio.SeqRecord import SeqRecord

def test_answer ():
    records = align.getAlignedSeq("12S")
    assert len(records) == 7
    for rec in records:
        assert isinstance(rec, SeqRecord)

def test_error ():
    with pytest.raises(Exception):
        align.getAlignedSeq("S")

