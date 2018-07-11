import sys 
sys.path.insert(0, '../src/')
from lapointe import *
import numpy as np
import pytest

def test_checkers():
    # Not Symmetric
    A = np.array([[0, 11, 5], [10 , 0, 4], [5, 4, 0]])
    with pytest.raises(Exception):
        _checkDMatrix(A)

    # Not square
    A =  np.array([ [0, 10, 5], [10 , 0, 4]])
    with pytest.raises(Exception):
        _checkDMatrix(A)

    # Different sizes
    A = np.array([[0, 11, 5], [10 , 0, 4], [5, 4, 0]])
    B = np.array([[0, 11], [11 , 0]])
    with pytest.raises(Exception):
        _checkDMatrixes(A, B)
    
def test_init():
    # Different Taxon_namespace
    with pytest.raises(Exception):
        ll = LL('../test/t1.nex', '../test/t6.nex')
        
    # Filetype not defined
    with pytest.raises(Exception):
        ll = LL('../test/t1.nex', '../test/t6.nex', f="ERROR")

def test_decomposition():
    dm = np.array([ [0, 10, 5], [10 , 0, 4], [5, 4, 0]])
    U, C = getDecomposition(dm)
    sub = dm - (U + C)
    assert ((np.min(sub) == 0) and (np.max(sub) == 0))

def test_standardize():
    dm = np.array([ [0, 10, 5], [10 , 0, 4], [5, 4, 0]])
    dm = standardize(dm)
    assert ((np.min(dm) == 0) and (np.max(dm) == 1))
    

def test_NISI():
    dm = np.array([ [0, 10, 5], [10 , 0, 4], [5, 4, 0]])
    dm = standardize(dm)
    # assert (NISI(dm, dm) == 1.0)

def test_SSD():
    A = np.array([[0, 10, 5], [10 , 0, 4], [5, 4, 0]])
    B = np.array([[0, 11, 5], [11 , 0, 4], [5, 4, 0]])
    C = np.array([[0, 1, 32], [1 , 0, 8], [32, 8, 0]])
    A = standardize(A)
    B = standardize(B)
    C = standardize(C)
    
    assert (SSD(A, A) == 0.0)
    assert (SSD(A, B) < SSD(A, C))


