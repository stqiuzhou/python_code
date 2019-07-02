#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = remove_inv_bar_ctoh.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/27 13:37


from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
from matplotlib.dates import num2date
from fvcom_tools_packages.fvcom_prep import FvcomPrep
import numpy as np
from scipy.interpolate import griddata, interp1d

## 数据准备
# 高度计
alti_path = r'E:\altimeter_data\ctoh.sla.ref.TP.chinasea.088.nc'
alti_data = ReadData(alti_path, types='alti',
                     alti_cycle=[38, 39, 40])
alti_sla = alti_data.data.alti_sla[alti_data.data.alti_sla.mask == False]
alti_time = alti_data.data.alti_time[alti_data.data.alti_sla.mask == False]
alti_lon = alti_data.data.alti_lon[alti_data.data.alti_sla.mask == False]
alti_lat = alti_data.data.alti_lat[alti_data.data.alti_sla.mask == False]
# 简单看下高度计轨迹 (判断读取的对不对)
alti_plot = PlotFigure(extents=[105, 135, 5, 40], depth=True, tick_inc=[5, 4])
alti_plot.plot_lines(alti_data.data.alti_lon, alti_data.data.alti_lat,
                     color='r', lw=3)
alti_plot.show()

# ecmwf
ecmwf_path = r'E:\ecmwf\press\1993\interim_press1993_10.nc'
press_data = ReadData(ecmwf_path, 'ecmwf',
                      variables=['lon', 'lat', 'time', 'slp'],
                      extents=[np.min(alti_lon)-1, np.max(alti_lon)+1,
                               np.min(alti_lat)-1, np.max(alti_lat)+1])


## ecmwf插值到高度计上
interped_obj = FvcomPrep()
interped_pressure = interped_obj.interp_temp_spatial(press_data.data.lon, press_data.data.lat,
                                               press_data.data.time, press_data.data.slp,
                                               alti_lon, alti_lat, alti_time, time_single=True)

# 减去逆气压影响
IB = -9.948 * (interped_pressure - 101325) * 0.01  # 单位 mm
elevation = alti_sla - IB * 0.001

# 画图
sla_plot = PlotFigure(cartesian=True)
sla_plot.plot_lines(alti_lat, elevation)
sla_plot.show()

