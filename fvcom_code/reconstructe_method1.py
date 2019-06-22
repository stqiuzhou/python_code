#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = reconstructe_method1.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/20 9:22

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.reconstructe_wind import Reconstructe
from fvcom_tools_packages.fvcom_prep import FvcomPrep
from fvcom_tools_packages.fvcom_grid import Grid
from fvcom_tools_packages.fvcom_plot import PlotFigure
from matplotlib.dates import num2date
import numpy as np

"""
    方法：气压场采用Fujita公式，然后计算梯度风，叠加ueno的移动风场来重构风场
          重构部分的风场替换掉之前生成的表明风场驱动（气压场同样操作）
          为了做敏感性实验，重构风场和气压场以后都设为0
"""

# 台风最佳路径数据
# # 1997年WINNIE
# tp_track_path = r'H:\best_track\CH\CH1997BST.txt'
# tp_track_data = ReadData(tp_track_path, str_before='WINNIE', str_after='WINNIE(-)1', types='ch')
# 1993年Flo
tp_track_path = r'H:\best_track\CH\CH1993BST.txt'
tp_track_data = ReadData(tp_track_path, str_before='Flo', str_after='Gene', types='ch')

# ecmwf 生成的表明风场和气压驱动
old_file_path = r'H:\fvcom\fvcom_input_file\ecmwf_08_10.nc'
fvcom_data = ReadData(old_file_path, variables=['wind', 'slp'])
fvcom_data.read_fvcom_nc()
fvcom_data.data.slp[:] = 101325
fvcom_data.data.uwnd[:] = 0
fvcom_data.data.vwnd[:] = 0



# 重构风场
# 所求风场点的经纬度
lon = fvcom_data.data.lonc
lat = fvcom_data.data.latc
lon1 = fvcom_data.data.lon
lat1 = fvcom_data.data.lat
# 某个台风中心经纬度、气压和最大风速，i代表第i+1个
for i in range(len(tp_track_data.data.tp_lon)-1):

    lonc = tp_track_data.data.tp_lon[i]
    latc = tp_track_data.data.tp_lat[i]
    Pc = tp_track_data.data.tp_press[i]
    P1 = 1013.25   # 外围气压
    Vmax = tp_track_data.data.tp_vmax[i]
    lonc_af = tp_track_data.data.tp_lon[i+1]
    latc_af = tp_track_data.data.tp_lat[i+1]
    dt = 6
    theta = 20  # 台风入流角

    reconstruct_wind1 = Reconstructe(lon1, lat1, lonc, latc, Pc, P1,
                                Vmax, lonc_af, latc_af, dt, theta, Rk=40)

    reconstruct_wind = Reconstructe(lon, lat, lonc, latc, Pc, P1,
                                Vmax, lonc_af, latc_af, dt, theta, Rk=40)
    uwind, vwind, wind = reconstruct_wind.synthesis_windfield(c1=0.5, c2=0.9)

    # 替换对应时间的气压值和风场值
    tp_time = tp_track_data.data.tp_time[i]
    time_index = np.where(tp_time == fvcom_data.data.time)[0][0]
    fvcom_data.data.slp[time_index, :] = reconstruct_wind1.Pr * 100
    fvcom_data.data.uwnd[time_index, :] = uwind
    fvcom_data.data.vwnd[time_index, :] = vwind

    # # 画风场图
    # plot = PlotFigure(grid_path=grid_path, figsize=(12, 8), title='method1_reconstruction', extents=[105, 135, 5, 40])
    # img = plot.plot_field_based_grid(wind)
    # plot.show()

# 网格数据路径
grid_path = r'H:\fvcom\fvcom_input_file\sms.2dm'
# 表面强迫的nc输出
prep = FvcomPrep(grid_path)
ptime = num2date(fvcom_data.data.time)
prep.write_surface_forcing(r'H:\fvcom\fvcom_input_file\ecmwf_08_10_rec1.nc',
                           ptime, fvcom_data.data)
