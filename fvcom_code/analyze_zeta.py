#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = analyze_zeta.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/23 19:05

from fvcom_tools_packages.fvcom_post import FvcomPost
from fvcom_tools_packages.fvcom_plot import PlotFigure
"""
    功能：分析fvcom模式增水
"""

# 数据准备
# wind_result = r'H:\fvcom\fvcom_output_file\windECMWF.nc'
wind_result = r'H:\fvcom\fvcom_output_file\MwindIB_0001.nc'
# wind_result = r'D:\2018_2019_research\china_sea_1993\fvcom_output\cswind_adjusted0001.nc'
# wind_result = r'H:\fvcom\fvcom_output_file\wind_0001.nc'
tide_result = r'H:\fvcom\fvcom_output_file\Atide_0001.nc'
xm_station = (118.04, 24.27)
start_time = '1993-09-23 00:00:00'
end_time = '1993-10-12 00:00:00'
# 计算由于风引起的增水
zeta_obj = FvcomPost(tide_path=tide_result, wind_path=wind_result)
zeta = zeta_obj.calculate_model_zeta(xm_station, start_time, end_time)
# 画图



