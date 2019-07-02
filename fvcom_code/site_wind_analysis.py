#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = site_wind_analysis.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/28 13:29

from fvcom_tools_packages.fvcom_plot import PlotFigure
import pandas as pd
import numpy as np
from datetime import datetime
from matplotlib.dates import date2num, DateFormatter
import matplotlib.pyplot as plt

# 数据准备
# site_wind_path = r'E:\site_data\yjs_sql\shengsi.xlsx'
# site_wind_path = r'E:\site_data\yjs_sql\shipu.xlsx'
# site_wind_path = r'E:\site_data\yjs_sql\dachen.xlsx'
site_wind_path = r'E:\site_data\yjs_sql\yuhuan.xlsx'
station = site_wind_path.split('\\')[-1][0:-5]
site_wind_data = pd.read_excel(site_wind_path, sheet_name='wind')
time_str = site_wind_data['time'].astype(str)
time = [datetime.strptime(x, '%Y%m%d%H') for x in time_str]
time_stamp = date2num(time)
wind_spd = site_wind_data['wind_spd'].to_numpy()
wind_dir = site_wind_data['wind_dir'].to_numpy()
# 数据中的角度和quiver的角度不一样，需要加180度
wind_dir = wind_dir + 180
# 选择数据
start_time = date2num(datetime(1993, 9, 28, 2))
end_time = date2num(datetime(1993, 10, 12, 14))
start_index = np.where(start_time == time_stamp)[0][0]
end_index = np.where(end_time == time_stamp)[0][0]
select_wind_spd = wind_spd[start_index:end_index+1]
select_wind_dir = wind_dir[start_index:end_index+1]
select_wind_time = time_stamp[start_index:end_index+1]

# # 画风向时间序列图
# plot_obj = PlotFigure(figsize=(12, 6),cartesian=True, title='Da Chen')
# plot_obj.plot_windDir_time(select_wind_time, select_wind_spd, select_wind_dir)
# output_name = r'D:\2018_2019_research\china_sea_1993\images\papar_images\site_station\{}.pdf'.format(station)
# # plot_obj.save(output_name)
# plot_obj.show()

# 画风速时间序列图
spd_plot = PlotFigure(cartesian=True, title='Yu Huan', grid=True, y_label='Wind Speed(m/s)')
spd_plot.plot_lines(select_wind_time, select_wind_spd, time_series=True)
output_name = r'D:\2018_2019_research\china_sea_1993\images\papar_images\site_station\{}_spd.pdf'.format(station)
spd_plot.save(output_name)
# spd_plot.show()


