#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = plot_research_region.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/11 10:14

from fvcom_tools_packages.fvcom_plot import PlotFigure
from fvcom_tools_packages.read_data import ReadData
import numpy as np
from matplotlib.dates import num2date

"""
    功能：绘制研究区域（包含台风路径、高度计路径以及验潮站）
"""

# %% 数据准备
altimeter_path = r'E:\altimeter_data\ctoh.sla.ref.TP.chinasea.088.nc'
typhoon_path = r'E:\best_track\bwp1993\bwp261993.txt'
alti_data = ReadData(altimeter_path, types='alti', alti_cycle=39)
tp_data = ReadData(typhoon_path, types='bwp')

# %% 画图
plot_obj = PlotFigure(figsize=(10, 8), extents=[115, 138, 15, 35],
                      depth=True, tick_inc=[4, 4])
# 高度计轨迹
plot_obj.plot_lines(alti_data.data.alti_lon, alti_data.data.alti_lat,
                    color='r', lw=4)
# 台风轨迹
plot_obj.plot_lines(tp_data.data.tp_lon, tp_data.data.tp_lat,
                    color='k', marker='o', mfc='r', mec='b',
                    lw=4, ms=10)
# 添加部分台风时间
for i in range(32, 42, 2):
    plot_obj.text(tp_data.data.tp_lon[i] + 0.5, tp_data.data.tp_lat[i] - 0.5,
                  num2date(tp_data.data.tp_time[i]).strftime('%m/%d/%HZ'))
# 验潮站位置
xiamen_loc = (118.08, 24.48)
kanmen_loc = (121.23, 28.13)
plot_obj.mark_location(xiamen_loc[0], xiamen_loc[1], name='XM')
plot_obj.mark_location(kanmen_loc[0], kanmen_loc[1], name='KM')
# 高度计捕捉到增水时刻台风的位置
alti_zeta_time = \
alti_data.data.alti_time[alti_data.data.alti_sla.mask == False][-1]
indx = np.argmin(np.abs(tp_data.data.tp_time - alti_zeta_time))
plot_obj.mark_location(tp_data.data.tp_lon[indx], tp_data.data.tp_lat[indx],
                       color='r', marker='^')
# 勾勒福建省界
plot_obj.fill_region(city='Fujian')
output = r'D:\2018_2019_research\china_sea_1993\images\final\regional.svg'
plot_obj.save(output, dpi=300)
plot_obj.show()
