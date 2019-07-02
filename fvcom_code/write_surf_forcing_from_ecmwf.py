#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = write_surf_forcing_from_ecmwf.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/17 14:40

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_prep import FvcomPrep
from fvcom_tools_packages.utily import PassiveStore
import os
import matplotlib.dates as pltdate
from fvcom_tools_packages.fvcom_plot import PlotFigure
import numpy as np
"""
    功能：表面强迫的nc输入，包括风场和气压场，数据来源ECMWF。
"""
# 列出需要读取ecmwf数据的路径
ecmwf_wind_dir = r'E:\ecmwf\wind\1993'
ecmwf_wind_files = os.listdir(ecmwf_wind_dir)
select_ecmwf_wind_path = [os.path.join(ecmwf_wind_dir, x) for x in ecmwf_wind_files[7:10]]

ecmwf_slp_dir = r'E:\ecmwf\press\1993'
ecmwf_slp_files = os.listdir(ecmwf_slp_dir)
select_ecmwf_slp_path = [os.path.join(ecmwf_slp_dir, x) for x in ecmwf_slp_files[7:10]]

# 读取数据
ecmwf_wind_data = ReadData(select_ecmwf_wind_path, types='ecmwf',
                      variables=['lon','lat', 'time', 'wind'],
                      extents=[105, 135, 5, 45])
ecmwf_slp_data = ReadData(select_ecmwf_slp_path, types='ecmwf',
                          variables=['time', 'slp'],
                          extents=[105, 135, 5, 45])
ecmwf_data = PassiveStore()
setattr(ecmwf_data, 'lon', ecmwf_wind_data.data.lon)
setattr(ecmwf_data, 'lat', ecmwf_wind_data.data.lat)
setattr(ecmwf_data, 'time', ecmwf_wind_data.data.time)
setattr(ecmwf_data, 'u10', ecmwf_wind_data.data.u10)
setattr(ecmwf_data, 'v10', ecmwf_wind_data.data.v10)
setattr(ecmwf_data, 'slp', ecmwf_slp_data.data.slp)
ptime = pltdate.num2date(ecmwf_data.time, tz=None)
ecmwf_wind_speed = np.sqrt(ecmwf_data.u10 ** 2 + ecmwf_data.v10 ** 2)
# # 插值前ecmwf画图
X, Y = np.meshgrid(ecmwf_data.lon, ecmwf_data.lat)
ecmwf_plot = PlotFigure(extents=[105, 135, 5, 45],
                       title='ecmwf')
ecmwf_plot.plot_surface(X, Y, ecmwf_wind_speed[0, :, :])
ecmwf_plot.show()
# 网格数据路径
grid_path = r'H:\fvcom\fvcom_input_file\sms.2dm'
# 表面强迫的插值
prep = FvcomPrep(grid_path)
interped_data = prep.interp_surface_forcing(ecmwf_data)
wind_speed = np.sqrt(interped_data.uwnd ** 2 + interped_data.vwnd ** 2)
# 插值后ncep画图
fig_obj = PlotFigure(grid_path=grid_path, figsize=(12, 8),
                     extents=[105, 135, 5, 45])
fig_obj.plot_surface(fig_obj.grid.lon, fig_obj.grid.lat, wind_speed[0, :])
fig_obj.show()
# 表面强迫的nc写入
prep.write_surface_forcing(r'H:\fvcom\fvcom_input_file\ecmwf_08_10_wnd.nc',
                           ptime, interped_data)

