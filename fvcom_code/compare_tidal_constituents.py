#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = compare_tidal_constituents.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/16 20:44

"""
    比较模式和验潮站的调和常数
"""
from fvcom_tools_packages.read_data import ReadData
from ttide import t_tide

# %% 数据准备
gauge_path = r'E:\gauge_data\h376a93.dat'  # 376表示厦门，632表示坎门
gauge_data = ReadData(gauge_path, types='gauge')
gauge_position = (118.04, 24.27)  # 厦门地理坐标(118.04, 24.27)，坎门的为(121.169, 28.053)
model_path = r'E:\fvcom\fvcom_output_file\AtideIB_0001.nc'
model_data = ReadData(model_path, types='fvcom', variables=['zeta'])
indx = model_data.find_nearest_point('zeta', gauge_position)
# %% 调和分析
# 验潮站
elev_anomaly = gauge_data.data.elev / 1000 - 3.281  # 3.281表示厦门的海平参考面，坎门的为3.87
gauge_xout = t_tide(elev_anomaly, stime=gauge_data.data.time[0],
              lat=gauge_position[1])
# 模式
xiamen_model_elev = model_data.data.zeta[:, indx].flatten()
fvcom_xout = t_tide(xiamen_model_elev, stime=model_data.data.time[0],
                    lat=gauge_position[1])
