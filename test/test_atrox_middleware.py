import sys
sys.path.insert(0, '../src/')
import atrox_middleware as at_mw
import pytest

def test_getPeptidesData():
    records = at_mw._getPeptides()
    for rec in records:
        for i in records[rec]:
            assert (i == '0' or i == '1')

def test_getPeptidesTypes():
    rec = at_mw._getPeptides()
    assert len(rec) == 4
    rec = at_mw._getPeptides("R")
    assert len(rec) == 8


