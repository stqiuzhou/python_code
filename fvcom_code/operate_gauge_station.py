#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = operate_gauge_station.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/12 13:24

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
import pandas as pd
from matplotlib.dates import date2num
from datetime import datetime
import numpy as np
from ttide import t_tide
from scipy.interpolate import interp1d

"""
    功能：处理验潮站数据，并画图
"""

# %% 数据准备
gauge_path = r'E:\gauge_data\h632a93.dat'  # 376表示厦门，632表示坎门
gauge_data = ReadData(gauge_path, types='gauge')
gauge_position = (121.169, 28.053)  # 厦门地理坐标(118.04, 24.27)，坎门的为(121.169, 28.053)
# %% 调和分析
elev_anomaly = gauge_data.data.elev / 1000 - 3.87  # 3.281表示厦门的海平参考面，坎门的为3.87
xout = t_tide(elev_anomaly, stime=gauge_data.data.time[0],
              lat=gauge_position[1])
gauge_zeta = elev_anomaly - xout(gauge_data.data.time)
# %% 筛选数据
select_time = pd.date_range('1993-09-28 00:00:00',
                            '1993-10-12 00:00:00',
                            freq='H')
select_time_stamp = date2num(select_time)
select_start_indx = np.where(gauge_data.data.time == select_time_stamp[0])[0][0]
select_end_indx = np.where(gauge_data.data.time == select_time_stamp[-1])[0][0]
select_gauge_zeta = gauge_zeta[select_start_indx:select_end_indx + 1]
# %% 验潮站相对于高度计过境时间时的增水和前期最大增水）
alti_pass_time = datetime(1993, 10, 8, 8, 32)
alti_pass_date = alti_pass_time.strftime('%m-%dT%H:%M')
alti_pass_stime = date2num(alti_pass_time)
zeta_func = interp1d(select_time_stamp, select_gauge_zeta)
gauge_zeta_alti = zeta_func(alti_pass_stime)
point_first = 46 # 62手动选出厦门的第一个峰值的点，坎门的是46
# %% 画图
plot_obj = PlotFigure(cartesian=True, grid=True,
                      y_label='Sea Level Anomalies(m)',
                      time_interval=2,
                      extents=[select_time_stamp[0],select_time_stamp[-1],
                               -0.2, 0.8])
plot_obj.plot_lines(select_time_stamp, select_gauge_zeta,
                    time_series=True, color='b')
plot_obj.vline(alti_pass_stime)
plot_obj.vline(select_time_stamp[point_first])
plot_obj.annotate(alti_pass_date, xy=(alti_pass_stime, gauge_zeta_alti),
                  xytext=(alti_pass_stime + 1, gauge_zeta_alti + 0.1))
plot_obj.annotate(select_time[point_first].strftime('%m-%dT%H:%M'),
                  xy=(select_time_stamp[point_first], select_gauge_zeta[point_first]),
                  xytext=(
                  select_time_stamp[point_first] + 1, select_gauge_zeta[point_first] + 0.1))
out_put = r'D:\2018_2019_research\china_sea_1993\images\final\before\gauge_xiamen.svg'
plot_obj.save(out_put)
plot_obj.show()
