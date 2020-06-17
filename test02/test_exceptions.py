# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:43:26 2020

@author: Administrator
"""


import pytest

def test_add_raises():
    '''测试一个肯定会报ValueError异常的用例'''
    str_to_change = '非数字字符不能转数字'
    with pytest.raises(ValueError):#预期下面的代码会抛ValueError
        num = int(str_to_change)