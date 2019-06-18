#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = utily.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/12 8:54

class PassiveStore(object):
    def __init__(self):
        pass

    def __iter__(self):
        return (a for a in self.__dict__.keys() if not a.startswith('_'))

def find_same_index(data):
    if isinstance(data, list):
        x = data
    else:
        x = list(data)
    index = []
    same_value = []
    for idx, ivalue in enumerate(x):
        if x.count(ivalue) > 1:
            index.append(idx)
            same_value.append(ivalue)
    return index, same_value



