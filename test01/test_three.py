# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:08:25 2020

@author: Administrator
"""

import pytest

def add(x, y):
    return (x + y)

def test_add_1():
    assert add(1, 2) == 3
    
def test_add_2():
    assert add(2, 2) == add(1,4)
    
