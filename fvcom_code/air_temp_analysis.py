#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = air_temp_analysis.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/3 9:23

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
import os
from datetime import datetime
from matplotlib.dates import date2num, num2date
import numpy as np

# 数据准备(采用的是ECMWF的2m气温)
temp_path_dir = r'E:\ecmwf\temp\1993'
temp_filename = os.listdir(temp_path_dir)
temp_path = [os.path.join(temp_path_dir, x) for x in temp_filename[7: 10]]
temp_data = ReadData(temp_path, types='ecmwf',
                     variables=['lon', 'lat', 'time', 't2m', 'sst'],
                     extents=[105, 135, 5, 40])

# 选择画图的时间范围
start_time = datetime(1993, 9, 25, 0)
end_time = datetime(1993, 10, 12, 18)
start_time_stamp = date2num(start_time)
end_time_stamp = date2num(end_time)
start_indx = np.where(start_time_stamp == temp_data.data.time)[0][0]
end_indx = np.where(end_time_stamp == temp_data.data.time)[0][0]
select_t2m = temp_data.data.t2m[start_indx:end_indx + 1, :, :]
select_sst = temp_data.data.sst[start_indx:end_indx + 1, :, :]
select_time = temp_data.data.time[start_indx:end_indx + 1]

# 作图
for itime in range(len(select_time)):
    title = num2date(select_time[itime]).strftime('%Y-%m-%dT%H')
    temp_plot = PlotFigure(extents=[110, 135, 15, 40], tick_inc=[4, 5],
                           title=title, cb_label='℃', cb_lim=[18, 36])
    temp_plot.plot_surface(temp_data.data.lon, temp_data.data.lat,
                           select_t2m[itime, :, :])
    temp_plot.fill_region(city='Fujian', taiwan=True)
    out_dir = r'D:\2018_2019_research\china_sea_1993\images\papar_images\ecmwf_t2m'
    outname = 't2m' + num2date(select_time[itime]).strftime('%Y%m%dT%H') + '.png'
    out_path = os.path.join(out_dir, outname)
    temp_plot.save(out_path, dpi=300)
    # temp_plot.show()

