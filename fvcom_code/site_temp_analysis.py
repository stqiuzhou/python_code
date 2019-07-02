#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = site_temp_analysis.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/1 12:46

import pandas as pd
from datetime import datetime
from matplotlib.dates import date2num
from fvcom_tools_packages.fvcom_plot import PlotFigure
import numpy as np

# 温度和气压数据准备
# site_path = r'E:\site_data\yjs_sql\shengsi.xlsx'
# site_path = r'E:\site_data\yjs_sql\shipu.xlsx'
# site_path = r'E:\site_data\yjs_sql\dachen.xlsx'
site_path = r'E:\site_data\yjs_sql\yuhuan.xlsx'
station = site_path.split('\\')[-1][0:-5]
site_temp_data = pd.read_excel(site_path, sheet_name='temp')
site_press_data = pd.read_excel(site_path, sheet_name='pressure')
time_str = site_temp_data['time'].astype(str)
time = [datetime.strptime(x, '%Y%m%d%H') for x in time_str]
time_stamp = date2num(time)
# 温度
temp = site_temp_data['temp'].to_numpy()
max_temp = site_temp_data['max_temp'].to_numpy()
min_temp = site_temp_data['min_temp'].to_numpy()
# 气压
press = site_press_data['pressure'].to_numpy()
max_press = site_press_data['max_pressure'].to_numpy()
min_press = site_press_data['min_pressure'].to_numpy()

# 数据选择
start_time = date2num(datetime(1993, 9, 28, 2))
end_time = date2num(datetime(1993, 10, 12, 14))
start_index = np.where(start_time == time_stamp)[0][0]
end_index = np.where(end_time == time_stamp)[0][0]
select_temp = temp[start_index:end_index+1]
select_max_temp = max_temp[start_index:end_index+1]
select_min_temp = min_temp[start_index:end_index+1]
select_time = time_stamp[start_index:end_index+1]
select_press = press[start_index:end_index+1]
select_max_press = max_press[start_index:end_index+1]
select_min_press = min_press[start_index:end_index+1]

# Temp-Press画图
TP_plot = PlotFigure(cartesian=True, title='Yu Huan', y_label='Temperature(℃)', grid=True,
                           legend_label=('Temperture', 'Pressure'))
TP_plot.plot_lines(select_time, select_temp, time_series=True,
                         double_yaxis=True, double_y=select_press, double_ylabel='Air Pressure(hPa)')
output_name = r'D:\2018_2019_research\china_sea_1993\images\papar_images\site_station\{}_TP.pdf'.format(station)
# TP_plot.save(output_name)
TP_plot.show()

# Max_temp画图
MT_plot = PlotFigure(cartesian=True, title='Yu Huan', y_label='Temperature(℃)', grid=True)
time_delta = date2num(datetime(1993, 9, 28, 2)) - date2num(datetime(1993, 9, 28))
MT_plot.plot_lines(select_time[::4] - time_delta, select_max_temp[::4], time_series=True)
output_name = r'D:\2018_2019_research\china_sea_1993\images\papar_images\site_station\{}_max_tmp.pdf'.format(station)
# MT_plot.save(output_name)
MT_plot.show()

# Min_temp画图
MinT_plot = PlotFigure(cartesian=True, title='Yu Huan', y_label='Temperature(℃)', grid=True)
MinT_plot.plot_lines(select_time[::4] - time_delta, select_min_temp[::4], time_series=True)
output_name = r'D:\2018_2019_research\china_sea_1993\images\papar_images\site_station\{}_min_tmp.pdf'.format(station)
# MinT_plot.save(output_name)
MinT_plot.show()