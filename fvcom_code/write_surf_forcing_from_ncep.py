#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = write_surf_forcing_from_ncep.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/24 15:31 

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_prep import FvcomPrep
from fvcom_tools_packages.utily import PassiveStore
from fvcom_tools_packages.fvcom_plot import PlotFigure
import os
import matplotlib.dates as pltdate
import numpy as np

"""
    功能：表面强迫的nc输入，包括风场和气压场，数据来源NCEP。
"""
# 列出需要读取ncep数据的路径
ncep_wind_dir = r'H:\ncep\uv\1993'
ncep_wind_files = os.listdir(ncep_wind_dir)
select_ncep_wind_path = [os.path.join(ncep_wind_dir, x) for x in ncep_wind_files[:]]

ncep_slp_dir = r'H:\ncep\pressure\1993'
ncep_slp_files = os.listdir(ncep_slp_dir)
select_ncep_slp_path = [os.path.join(ncep_slp_dir, x) for x in ncep_slp_files[:]]

# 读取数据
ncep_wind_data = ReadData(select_ncep_wind_path, types='ncep',
                      variables=['lon','lat', 'time', 'wind'],
                      extents=[105, 135, 5, 45])
ncep_slp_data = ReadData(select_ncep_slp_path, types='ncep',
                          variables=['time', 'slp'],
                          extents=[105, 135, 5, 45])
ncep_data = PassiveStore()
setattr(ncep_data, 'lon', ncep_wind_data.data.lon)
setattr(ncep_data, 'lat', ncep_wind_data.data.lat)
setattr(ncep_data, 'time', ncep_wind_data.data.time)
setattr(ncep_data, 'u10', ncep_wind_data.data.u10)
setattr(ncep_data, 'v10', ncep_wind_data.data.v10)
setattr(ncep_data, 'slp', ncep_slp_data.data.slp)
ptime = pltdate.num2date(ncep_data.time, tz=None)
ncep_wind_speed = np.sqrt(ncep_data.u10 ** 2 + ncep_data.v10 ** 2)
# # 插值前ncep画图
X, Y = np.meshgrid(ncep_data.lon, ncep_data.lat)
ncep_plot = PlotFigure(extents=[105, 135, 5, 45],
                       title='ncep')
ncep_plot.plot_surface(X, Y, ncep_wind_speed[0, :, :])
ncep_plot.show()

# 网格数据路径
grid_path = r'H:\fvcom\fvcom_input_file\sms.2dm'
# 表面强迫的插值
prep = FvcomPrep(grid_path)
interped_data = prep.interp_surface_forcing(ncep_data)
wind_speed = np.sqrt(interped_data.uwnd ** 2 + interped_data.vwnd ** 2)
# 插值后ncep画图
fig_obj = PlotFigure(grid_path=grid_path, figsize=(12, 8),
                     extents=[105, 135, 5, 45])
fig_obj.plot_surface(fig_obj.grid.lon, fig_obj.grid.lat, wind_speed[0, :])
fig_obj.show()
# 表面强迫的nc写入
prep.write_surface_forcing(r'H:\fvcom\fvcom_input_file\ncep_08_10_wnd.nc',
                           ptime, interped_data)
