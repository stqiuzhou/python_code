#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = utily.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/12 8:54

import numpy as np

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

def distance_on_sphere(lon1, lat1, lon2, lat2):
    """
    功能：计算两个经纬度之间的距离
    :param lon1:
    :param lat1:
    :param lon2:
    :param lat2:
    :return: distance 距离，单位为米
    """
    # 将度数转化为弧度
    radlon1, radlat1, radlon2, radlat2 = map(np.deg2rad,
                                             [lon1, lat1, lon2, lat2])
    a = radlat1 - radlat2
    b = radlon1 - radlon2
    r = 6371000
    distance = 2 * np.arcsin(np.sqrt(np.power(np.sin(a / 2), 2)
                              + np.cos(radlat1) * np.cos(radlat2) * np.power(np.sin(b / 2), 2))) * r
    return distance


