#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = match_model_site_wind.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/2 9:21

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
import pandas as pd
from scipy.interpolate import interp1d
import numpy as np
from datetime import datetime
from matplotlib.dates import date2num

# %% 数据准备
site_path = r'E:\site_data\yjs_sql\shengsi.xlsx'
site_data = ReadData(site_path, variables=['wind'], types='site_excel')
model_wind_path = r'E:\fvcom\fvcom_input_file\ncep_08_10_wnd.nc'
model_wind_data = ReadData(model_wind_path, variables=['wind'], types='fvcom')

# %% model数据匹配site数据
# 站点经纬度
station_ll = (122.27, 30.44)  # shengsi
# station_ll = (121.57, 29.12)  # shipu
# station_ll = (121.54, 28.27)  # dachen
# station_ll = (121.16, 28.05)  # yuhuan
index_station = model_wind_data.find_nearest_point('u', station_ll)

# 时间插值
model_time = model_wind_data.data.time[:]
site_time = site_data.data.time[:]
func_u = interp1d(model_time, model_wind_data.data.uwnd[:, index_station])
model_uwinded = func_u(site_time)
func_v = interp1d(model_time, model_wind_data.data.vwnd[:, index_station])
model_vwinded = func_v(site_time)
model_winded = np.sqrt(model_uwinded ** 2 + model_vwinded ** 2)

# 选择数据范围
start_time = datetime(1993, 9, 28, 2)
start_time_stamp = date2num(start_time)
end_time = datetime(1993, 10, 12, 14)
end_time_stamp = date2num(end_time)
start_time_indx = np.where(site_time == start_time_stamp)[0][0]
end_time_indx = np.where(site_time == end_time_stamp)[0][0]
select_site_time = site_time[start_time_indx:end_time_indx+1]
select_site_wind_spd= site_data.data.wind_spd[start_time_indx:end_time_indx+1]
select_site_wind_dir= site_data.data.wind_dir[start_time_indx:end_time_indx+1]
select_model_uwind = model_uwinded[start_time_indx:end_time_indx+1]
select_model_vwind = model_vwinded[start_time_indx:end_time_indx+1]
select_model_wind = model_winded[start_time_indx:end_time_indx+1]

# 只比较风速大小
spd_plot = PlotFigure(title='Sheng Si', cartesian=True, grid=True,
                      y_label='Wind Speed(m/s)',
                      legend_label=('site', 'model'),
                      time_interval=2)
plot1 = spd_plot.scatter(select_site_time, select_site_wind_spd, c='r')
plot2 = spd_plot.plot_lines(select_site_time, select_model_wind,
                            time_series=True)
spd_plot.set_legend(plot1, plot2)
output_name = r'D:\2018_2019_research\china_sea_1993\images\final\before\{}_MSwind_ncep.svg'.format(site_data.data.station)
spd_plot.save(output_name)
spd_plot.show()

