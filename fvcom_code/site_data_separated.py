#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = site_data_analysis.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/27 22:17

import pandas as pd
import numpy as np

# 数据准备
site_path = r'E:\site_data\yjs_sql\data_1993.xlsx'
site_wind_data = pd.read_excel(site_path, sheet_name='wind')
site_pressure_data = pd.read_excel(site_path, sheet_name='pressure')
site_temp_data = pd.read_excel(site_path, sheet_name='temperature')
# 删除空格
site_wind_data['StationName'] = site_wind_data['StationName'].map(str.strip)
site_pressure_data['StationName'] = site_pressure_data['StationName'].map(str.strip)
site_temp_data['StationName'] = site_temp_data['StationName'].map(str.strip)
# 分离出每个站点的风场数据
# station = '嵊泗'
# station = '石浦'
# station = '大陈岛'
station = '玉环'
station_wind_data = site_wind_data.loc[site_wind_data['StationName'].isin([station])].reset_index(drop=True)
station_pressure_data = site_pressure_data.loc[site_pressure_data['StationName'].isin([station])].reset_index(drop=True)
station_temp_data = site_temp_data.loc[site_temp_data['StationName'].isin([station])].reset_index(drop=True)
# 提取站点的观测时间，以及风速风向
# 创建pd
station_wind_new = pd.DataFrame(columns=['time', 'wind_spd', 'wind_dir', 'wind_max_spd', 'wind_max_dir'])
#处理时间，并放置入新创建的pd
time_day = station_wind_data['the_year'].map(str) + station_wind_data['the_month'].map(str).str.zfill(2) + station_wind_data['the_day'].map(str).str.zfill(2)
time_hour = ['02', '08', '14']
station_time_tmp = []
for ihour in time_hour:
    time = time_day + ihour
    station_time_tmp.append(time)
station_time = [item for sublist in station_time_tmp for item in sublist]
station_wind_new['time'] = station_time
# 处理风速和风向
station_spd_02 = station_wind_data['sp02']
station_spd_08 = station_wind_data['sp08']
station_spd_14 = station_wind_data['sp14']
station_spd = [item for sublist in [station_spd_02, station_spd_08, station_spd_14] for item in sublist]
station_wind_new['wind_spd'] = np.asarray(station_spd) / 10
station_dir_02 = station_wind_data['dr02']
station_dir_08 = station_wind_data['dr08']
station_dir_14 = station_wind_data['dr14']
station_dir = [item for sublist in [station_dir_02, station_dir_08, station_dir_14] for item in sublist]
station_wind_new['wind_dir'] = station_dir
# 最大风向和最大风速
station_max_spd = station_wind_data['Maxsp']
station_max_dir = station_wind_data['Maxdr']
station_wind_new['wind_max_spd'] = station_max_spd / 10
station_wind_new['wind_max_dir'] = station_max_dir
# 按照时间排序
station_wind_new.sort_values('time', inplace=True)
station_wind_new.reset_index(drop=True, inplace=True)

# 提取气压相关信息
# 创建pd
station_pressure_new = pd.DataFrame(columns=['time', 'pressure', 'max_pressure', 'min_pressure', 'P'])
# 处理时间，并放置入新创建的pd
time_hour1 = ['02', '08', '14', '20']
station_time_tmp = []
for ihour in time_hour1:
    time = time_day + ihour
    station_time_tmp.append(time)
station_time = [item for sublist in station_time_tmp for item in sublist]
station_pressure_new['time'] = station_time
# 处理气压
station_press_02 = station_pressure_data['P02']
station_press_08 = station_pressure_data['P08']
station_press_14 = station_pressure_data['P14']
station_press_20 = station_pressure_data['P20']
station_press = [item for sublist in [station_press_02, station_press_08, station_press_14, station_press_20] for item in sublist]
station_pressure_new['pressure'] = np.asarray(station_press) / 10
station_max_press = station_pressure_data['PMax']
station_min_press = station_pressure_data['PMin']
station_mean_press = station_pressure_data['P']
station_pressure_new['max_pressure'] = station_max_press / 10
station_pressure_new['min_pressure'] = station_min_press / 10
station_pressure_new['P'] = station_mean_press / 10
# 按照时间排序
station_pressure_new.sort_values('time', inplace=True)
station_pressure_new.reset_index(drop=True, inplace=True)

# 处理温度
# 创建pd
station_temp_new = pd.DataFrame(columns=['time', 'temp', 'max_temp', 'min_temp', 'T'])
# 处理时间，并放置入新创建的pd
station_temp_new['time'] = station_time
# 处理气压
station_temp_02 = station_temp_data['T02']
station_temp_08 = station_temp_data['T08']
station_temp_14 = station_temp_data['T14']
station_temp_20 = station_temp_data['T20']
station_temp = [item for sublist in [station_temp_02, station_temp_08, station_temp_14, station_temp_20] for item in sublist]
station_temp_new['temp'] = np.asarray(station_temp) / 10
station_max_temp = station_temp_data['Tmax']
station_min_temp = station_temp_data['Tmin']
station_mean_temp = station_temp_data['T']
station_temp_new['max_temp'] = station_max_temp / 10
station_temp_new['min_temp'] = station_min_temp / 10
station_temp_new['T'] = station_mean_temp / 10
# 按照时间排序
station_temp_new.sort_values('time', inplace=True)
station_temp_new.reset_index(drop=True, inplace=True)
# 输出
output_path = r'E:\site_data\yjs_sql\yuhuan.xlsx'
writer = pd.ExcelWriter(output_path)
station_wind_new.to_excel(writer, index=False, sheet_name='wind')
station_pressure_new.to_excel(writer, index=False, sheet_name='pressure')
station_temp_new.to_excel(writer, index=False, sheet_name='temp')
writer.save()