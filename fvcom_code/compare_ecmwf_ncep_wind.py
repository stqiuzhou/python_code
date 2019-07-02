#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = compare_ecmwf_ncep_wind.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/24 14:42

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
import numpy as np
# 准备数据
ncep_path = r'H:\ncep\uv\splanl.gdas.19930801-19930805.grb2.nc'
ecmwf_path = r'E:\ecmwf\wind\1993\interim_uv1993_08.nc'
extents = [105, 135, 5, 40]
ncep_data = ReadData(ncep_path, types='ncep',
                     variables=['lon', 'lat', 'time', 'wind'],
                     extents=extents)
ncep_wind_speed = np.sqrt(ncep_data.data.u10[:] ** 2 +
                          ncep_data.data.v10[:] ** 2)
ecmwf_data = ReadData(ecmwf_path, types='ecmwf',
                     variables=['lon', 'lat', 'time', 'wind'],
                     extents=extents)
ecmwf_wind_speed = np.sqrt(ecmwf_data.data.u10[:] ** 2 +
                          ecmwf_data.data.v10[:] ** 2)
time_index = 0
# ncep画图
X, Y = np.meshgrid(ncep_data.data.lon, ncep_data.data.lat)
ncep_plot = PlotFigure(extents=extents, title='ncep')
ncep_plot.plot_surface(X, Y, ncep_wind_speed[0, :, :])
ncep_plot.show()
# ecmwf画图
X, Y = np.meshgrid(ecmwf_data.data.lon, ecmwf_data.data.lat)
ncep_plot = PlotFigure(extents=extents, title='ecmwf')
ncep_plot.plot_surface(X, Y, ecmwf_wind_speed[0, :, :])
ncep_plot.show()
