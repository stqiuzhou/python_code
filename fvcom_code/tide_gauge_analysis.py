#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = tide_gauge_analysis.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2018/12/28 20:45


import re
import os
import numpy as np
import pandas as pd
import utide
from matplotlib.dates import date2num, DateFormatter
import matplotlib.pylab as plt
import matplotlib.dates as dates
from scipy import interpolate
from datetime import datetime
from netCDF4 import num2date
import ttide
from PyFVCOM.read import FileReader
from fvcom_tools_packages.fvcom_post import FvcomPost

# fvcom
es_all = r'D:\2018_2019_research\china_sea_1993\fvcom_output\csall_bottom_0025.nc'
es_wind = r'D:\2018_2019_research\china_sea_1993\fvcom_output\cswind_bottom_0025.nc'
all_data = FileReader(es_all, variables=['zeta', 'time'])
wind_data = FileReader(es_wind, variables=['zeta', 'time'])

# gauge = (121.169, 28.053) # 121.169 28.053 # xm 118.04 24.27
gauge = (118.04, 24.27)
index = all_data.closest_node(gauge)
time = num2date(all_data.data.time[:], all_data.atts.Itime.units)
time_stamp = date2num(time)
select_time = pd.date_range('1993-09-28 00:00:00',
                            '1993-10-12 00:00:00',
                            freq='H')
select_time_stamp = date2num(select_time.to_pydatetime())
time_start = np.where(time_stamp == select_time_stamp[0])
time_end = np.where(time_stamp == select_time_stamp[-1])
zeta_wind = wind_data.data.zeta[int(time_start[0]):int(time_end[0]) + 1, index]  - all_data.data.zeta[int(time_start[0]):int(time_end[0]) + 1, index]
zeta_wind_de = zeta_wind - (wind_data.data.zeta - all_data.data.zeta).mean()
# gauge station
gauge_path = r'D:\2018_2019_research\china_sea_1993\gauge_data\h376a93.dat' # xiamen
# gauge_path = r'D:\2018_2019_research\china_sea_1993\gauge_data\h632a93.dat'   #kanmen
xiamen_data = pd.read_table(gauge_path, skiprows=[0], header=None, sep='\s+')
xiamen_data.drop([0, 1, 2], axis=1, inplace=True)
level_data = xiamen_data.values.flatten()
time_data = pd.date_range('1993-01-01 00:00:00',
                          '1993-12-31 23:00:00',
                          freq='H')
time_serial_data = pd.DataFrame({'elev': level_data}, index=time_data)
time_stamp1 = date2num(time_serial_data.index.to_pydatetime())
elev_anomaly = time_serial_data['elev'].values / 1000 - 3.281   #3.281 xiamen #3.87 kanmen

# se_time = pd.date_range('1993-08-01 00:00:00',
#                         '1993-10-31 00:00:00',
#                         freq='H')

time_gauge_start = np.where(time_stamp1 == time_stamp[0])
time_gauge_end = np.where(time_stamp1 == time_stamp[-1])

xout = ttide.t_tide(elev_anomaly, stime=time_stamp1[0], lat=np.array(24.27))


# select data
select_time = pd.date_range('1993-09-28 00:00:00',
                            '1993-10-12 00:00:00',
                            freq='H')
select_time_stamp = date2num(select_time.to_pydatetime())
elev_fit = xout(select_time_stamp)
mean_fit = xout(time_stamp)
time_start = np.where(time_stamp1 == select_time_stamp[0])
time_end = np.where(time_stamp1 == select_time_stamp[-1:])
select_zeta_gauge = (elev_anomaly[int(time_start[0]):int(time_end[0]+1)] - elev_fit)
mean_guage = elev_anomaly[int(time_gauge_start[0]):int(time_gauge_end[0]+1)] - mean_fit
mean_guage1 = mean_guage.mean()
select_zeta_gauge_de = select_zeta_gauge - mean_guage1

# select_zeta_gauge = zeta_gauge[int(time_start[0]):int(time_end[0]+1)]

wind_result = r'H:\fvcom\fvcom_output_file\MwindIB_0001.nc'
# wind_result = r'D:\2018_2019_research\china_sea_1993\fvcom_output\cswind_adjusted0001.nc'
# wind_result = r'H:\fvcom\fvcom_output_file\wind_0001.nc'
tide_result = r'H:\fvcom\fvcom_output_file\Atide_0001.nc'
xm_station = (118.04, 24.27)
start_time = '1993-09-28 00:00:00'
end_time = '1993-10-12 00:00:00'
# 计算由于风引起的增水
zeta_obj = FvcomPost(tide_path=tide_result, wind_path=wind_result)
zeta1 = zeta_obj.calculate_model_zeta(xm_station, start_time, end_time)

font1 = {'family': 'Times New Roman',
         'size': 12,
         'weight': 'bold'}
# 画图
figure = plt.figure(figsize=(10,6), dpi=600)
ax = figure.add_subplot(1, 1, 1)
# plt.ylim(0, 1.4)
# ax.plot(time_stamp, mean_guage, linestyle='-', color='b', linewidth='1')
ax.plot(select_time_stamp, select_zeta_gauge_de, linestyle='-', color='b', linewidth='1')
# plt.plot(select_time_stamp, zeta_wind, linestyle='-', color='r', linewidth='1' )
plt.plot(select_time_stamp, zeta_wind_de, linestyle='--', color='r', linewidth='1' )
plt.plot(select_time_stamp, zeta1, linestyle='--', color='k', linewidth='1' )

plt.xticks(fontname='Times New Roman', size=14)
plt.yticks(fontname='Times New Roman', size=14)
ax.xaxis.set_major_formatter(DateFormatter('%m/%d/%H'))
figure.autofmt_xdate()
# # ax.legend(prop={'size': 18})
# # altimeter pass time
# altimeter_time = '1993-10-08 08:32:46'
# altimeter_time_stamp = dates.date2num(datetime.strptime(altimeter_time, '%Y-%m-%d %H:%M:%S'))
# f = interpolate.interp1d(select_time_stamp, select_zeta_gauge, kind='cubic')
# ynew = f(altimeter_time_stamp)
# plt.axvline(x=altimeter_time_stamp, color='r', linestyle='--')
# plt.annotate(altimeter_time, xy=(altimeter_time_stamp, ynew),
#               xytext=(select_time_stamp[310], 1), arrowprops=dict(facecolor='black', shrink=0.01)) # -220 -30  # xiamen -10 35
plt.grid(True)
plt.show()


# plt.show()