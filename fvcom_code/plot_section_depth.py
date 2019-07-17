#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = plot_section_depth.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/15 15:57

"""
    功能：在研究区域上绘制断面，并且绘制横坐标为距离纵坐标为水深的断面图
"""

from fvcom_tools_packages.fvcom_plot import PlotFigure
from fvcom_tools_packages.utily import distance_on_sphere
from netCDF4 import Dataset
from scipy.interpolate import interp2d
import numpy as np

# %% 在研究区域上绘制断面
# 计算第一个横截面的经纬度
lon1 = [121.28, 125.67]
lat1 = [28.07, 25.87]
k1 = (lat1[0] - lat1[1]) / (lon1[0] - lon1[1])
b1 = lat1[0] - k1 * lon1[0]
LLon1 = np.arange(lon1[0], lon1[1], 0.02)
LLat1 = k1 * LLon1 + b1
# 计算第二个横截面的经纬度
lon2 = [120, 123.47]
lat2 = [26.61, 24.72]
k2 = (lat2[0] - lat2[1]) / (lon2[0] - lon2[1])
b2 = lat2[0] - k2 * lon2[0]
LLon2 = np.arange(lon2[0], lon2[1], 0.02)
LLat2 = k2 * LLon2 + b2
# # 画图
# plot_obj = PlotFigure(figsize=(10, 10), extents=[116, 128, 20, 32],
#                       depth=True, tick_inc=[2, 2],
#                       levels=[50, 100, 300, 500, 1500])
# plot_obj.plot_lines(LLon1, LLat1, color='r')
# plot_obj.plot_lines(LLon2, LLat2, color='r')
# # 勾勒福建省界和浙江省界
# plot_obj.fill_region(city='Fujian')
# plot_obj.fill_region(city='Zhejiang')
# output = r'D:\2018_2019_research\china_sea_1993\images\final\before\setion.svg'
# plot_obj.save(output, dpi=300)
# plot_obj.show()

# %% 画水深断面图
lat = LLat1
lon = LLon1
# 读取水深值
depth_file = r'H:\depth_data\ETOPO1.nc'
depth_data = Dataset(depth_file)
depth_lon = depth_data.variables['x'][:]
depth_lat = depth_data.variables['y'][:]
depth = depth_data.variables['z'][:]
# 选择指定区域
extents = [115, 138, 15, 35]
lat_index_down = np.where(depth_lat > extents[-2])[0][0]
lat_index_up = np.where(depth_lat < extents[-1])[0][-1]
lon_index_left = np.where(depth_lon > extents[0])[0][0]
lon_index_right = np.where(depth_lon < extents[1])[0][-1]
select_lat = depth_lat[lat_index_down:lat_index_up + 1]
select_lon = depth_lon[lon_index_left:lon_index_right + 1]
select_depth = depth[lat_index_down:lat_index_up + 1,
               lon_index_left:lon_index_right + 1]
# 插值水深
interp_depth = []
func = interp2d(select_lon, select_lat, select_depth)
for i in range(len(lat)):
    z = func(lon[i], lat[i])
    interp_depth.append(z)
# 计算距离
distance = []
for j in range(len(lat)):
    dis = distance_on_sphere(lon[0], lat[0], lon[j], lat[j]) / 1000
    distance.append(dis)
# 画图
plot_obj = PlotFigure(cartesian=True, x_label='Distance(km)',
                      y_label='Depth(m)', extents=[0, 500, -2500, 0])
plot_obj.plot_lines(distance, interp_depth)
plot_obj.plot_lines()
plot_obj.ax.xaxis.set_ticks_position('top')
plot_obj.ax.xaxis.set_label_position('top')
plot_obj.ax.spines['bottom'].set_visible(False)
plot_obj.ax.spines['right'].set_visible(False)

output = r'D:\2018_2019_research\china_sea_1993\images\final\before\section2.svg'
# plot_obj.save(output)
plot_obj.show()


