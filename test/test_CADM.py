import sys 
sys.path.insert(0, '../src/')
import CADM
import numpy as np
import pytest

def test_diffNtax() :
    with pytest.raises(Exception):
        CADM("../test/t1.nex", "../test/t3.nex")

def test_modes():
    with pytest.raises(Exception):
        CADM("../test/t1.nex", "../test/t2.nex", "-g")

