#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = compare_model_gauge.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/8 14:13

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
import numpy as np
import pandas as pd
import ttide
from datetime import datetime
from matplotlib.dates import num2date, date2num

"""
    功能：比较模式和验潮站的增水情况
"""

# %% 数据准备
gauge_path = r'E:\gauge_data\h632a93.dat'  # 376表示厦门，632表示坎门
model_wind_path = r'E:\fvcom\fvcom_output_file\windNCEP_0001.nc'
model_tide_path = r'E:\fvcom\fvcom_output_file\AtideIB_0001.nc'
position_site = (121.169, 28.053)  # 厦门地理坐标(118.04, 24.27)，坎门的为(121.169, 28.053)

# %% 模式数据处理
model_tide_data = ReadData(model_tide_path, types='fvcom',
                           variables=['zeta'])
model_wind_data = ReadData(model_wind_path, types='fvcom',
                           variables=['zeta'])
model_zeta = model_wind_data.data.zeta - model_tide_data.data.zeta
model_start_time = model_tide_data.data.time[0]
model_end_time = model_tide_data.data.time[-1]
gauge_indx = model_tide_data.find_nearest_point('zeta', position_site)
# 减去模式的平均值(减去的平均值是模式结果的整体平均，非个点)
specific_mzeta = model_zeta[:, gauge_indx] - model_zeta.mean()

# %% 验潮站数据处理
gauge_data = ReadData(gauge_path, types='gauge')
# 做调和分析
elev_anomaly = gauge_data.data.elev / 1000 - 3.87  # 3.281表示厦门的海平参考面，坎门的为3.87
xout = ttide.t_tide(elev_anomaly, stime=gauge_data.data.time[0],
                    lat=position_site[1])
gauge_zeta = elev_anomaly - xout(gauge_data.data.time)
# 计算模式时间范围的平均值（为了更好的和模式比较）
start_indx = np.where(gauge_data.data.time == model_start_time)[0][0]
end_indx = np.where(gauge_data.data.time == model_end_time)[0][0]
gauge_mean_zeta = np.mean(gauge_zeta[start_indx:end_indx + 1])

# %% 选择研究的时间范围
select_time = pd.date_range('1993-09-28 00:00:00',
                            '1993-10-12 00:00:00',
                            freq='H')
select_time_stamp = date2num(select_time)
# 选择时间范围的验潮站数据(减去平均)
select_start_indx = np.where(gauge_data.data.time == select_time_stamp[0])[0][0]
select_end_indx = np.where(gauge_data.data.time == select_time_stamp[-1])[0][0]
select_gauge_zeta = gauge_zeta[
                    select_start_indx:select_end_indx + 1] - gauge_mean_zeta
# 选择时间范围的模式数据（减去平均）
select_start_mindx = \
    np.where(model_tide_data.data.time == select_time_stamp[0])[0][0]
select_end_mindx = \
    np.where(model_tide_data.data.time == select_time_stamp[-1])[0][0]
select_model_zeta = specific_mzeta[select_start_mindx:select_end_mindx + 1]

# %% 画图
plot_obj = PlotFigure(cartesian=True, y_label='Sea Level Anomalies(m)',
                      legend_label=('Tide-Gauge', 'Model'), grid=True,
                      time_interval=2)
plot1 = plot_obj.plot_lines(select_time_stamp, select_gauge_zeta,
                            time_series=True, color='b')
plot2 = plot_obj.plot_lines(select_time_stamp, select_model_zeta,
                            linestyle='--', color='r')
plot_obj.set_legend(plot1, plot2)
output = r'D:\2018_2019_research\china_sea_1993\images\final\before\kanmen_gmzeta.svg'
plot_obj.save(output)
# plot_obj.show()
