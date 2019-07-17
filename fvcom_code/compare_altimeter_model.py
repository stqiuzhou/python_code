#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = compare_altimeter_model.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/4 15:13

"""
    功能：该代码主要用于比较模式和高度计的增水
"""
from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
from fvcom_tools_packages.fvcom_prep import FvcomPrep
import numpy as np
from datetime import datetime
from matplotlib.dates import date2num, num2date

# %% 数据准备
alti_path = r'E:\altimeter_data\ctoh.sla.ref.TP.chinasea.088.nc'
model_wind_path = r'E:\fvcom\fvcom_output_file\windNCEP_0001.nc'
model_tide_path = r'E:\fvcom\fvcom_output_file\AtideIB_0001.nc'

# %% 处理高度计数据（主要是减去三个月的平均值，更好的与模式比较）
alti_data = ReadData(alti_path, types='alti')
# 找出全部错误的pass
indx = np.where(alti_data.data.alti_time.max(axis=0) > 711957.9999)[0]
alti_time = alti_data.data.alti_time[:, indx]
alti_sla = alti_data.data.alti_sla[:, indx]
alti_cycle = alti_data.data.alti_cycle[indx]
# 所有pass的海面高度平均
all_pass_mean = np.mean(alti_sla, axis=1).shape
alti_sla = alti_sla[:,1] - all_pass_mean
# 选取8,9,10三个月的cycle，算出平均值
start_time = datetime(1993, 8, 1)
end_time = datetime(1993, 10, 31)
start_time_stamp = date2num(start_time)
end_time_stamp = date2num(end_time)
start_indx = np.where(alti_time.max(axis=0) >= start_time_stamp)[0][0]
end_indx = np.where(alti_time.max(axis=0) <= end_time_stamp)[0][-1]
select_alti_cycle = alti_cycle[start_indx:end_indx + 1]
select_alti_time = alti_time[:, start_indx:end_indx + 1]
select_alti_sla = alti_sla[:, start_indx:end_indx + 1]
# mean_alti_sla = np.mean(select_alti_sla, axis=1)
mean_alti_sla = np.mean(select_alti_sla)
# 只算前后2pass的平均值
alti_sla_38 = select_alti_sla[:, select_alti_cycle == 38].ravel()
alti_sla_40 = select_alti_sla[:, select_alti_cycle == 40].ravel()
alti_sla_39_temp = select_alti_sla[:, select_alti_cycle == 39].ravel()
mean_alti_sla_2 = (alti_sla_38 + alti_sla_40) / 2
# pass39 减去平均值
alti_sla_39_before = select_alti_sla[:, select_alti_cycle == 39].ravel()
alti_sla_39 = alti_sla_39_before - mean_alti_sla_2
alti_time_39 = select_alti_time[:, select_alti_cycle == 39].ravel()
# 选取lat部分数据
lat_indx = np.where(alti_data.data.alti_lat >= 18)[0][0]
select_alti_lat = alti_data.data.alti_lat[lat_indx:]
select_alti_lon = alti_data.data.alti_lon[lat_indx:]
select_alti_time_39 = alti_time_39[lat_indx:]
select_alti_sla_39 = alti_sla_39[lat_indx:]

# %% 处理模式数据
model_wind_data = ReadData(model_wind_path, types='fvcom',
                           variables=['zeta'])
model_tide_data = ReadData(model_tide_path, types='fvcom',
                           variables=['zeta'])
model_zeta = model_wind_data.data.zeta - model_tide_data.data.zeta
# 插值到高度计上，时间空间分别插值
# 插值前去除需要插值的高度计不好的数据
interp_alti_sla = select_alti_sla_39[select_alti_sla_39.mask == False]
interp_alti_time = select_alti_time_39[select_alti_sla_39.mask == False]
interp_alti_lon = select_alti_lon[select_alti_sla_39.mask == False]
interp_alti_lat = select_alti_lat[select_alti_sla_39.mask == False]
grid_path = r'E:\fvcom\fvcom_input_file\sms.2dm'
prep_obj = FvcomPrep(grid_path)
interped_zeta = prep_obj.interp_temp_spatial(model_wind_data.lon,
                                             model_wind_data.lat,
                                             model_wind_data.data.time,
                                             model_zeta,
                                             interp_alti_lon, interp_alti_lat,
                                             interp_alti_time, time_single=True,
                                             regular=False)
# 计算出模式中对于高度计点的三个月平均值，并计算最后的模式zeta
position_indx = np.ones(len(interp_alti_lat))
i = 0
for ilon, ilat in zip(interp_alti_lon, interp_alti_lat):
    position = (ilon, ilat)
    indx_tmp = prep_obj.find_nearest_point('zeta', position)
    position_indx[i] = indx_tmp.astype(int)
    i += 1
select_zeta = np.asarray([model_zeta[:, x.astype(int)] for x in position_indx])
mean_zeta = np.mean(select_zeta, axis=1)
model_final_zeta = interped_zeta - np.mean(model_zeta)

# %% 画图
plot_obj = PlotFigure(cartesian=True, x_label='Latitude(deg N)',
                      y_label='Sea Surface Height Anomalies (m)',
                      legend_label=('CTOH', 'Model'))
plot_obj.plot_lines(interp_alti_lat, model_final_zeta)
plot_obj.plot_lines(select_alti_lat, select_alti_sla_39)
plot_obj.show()
