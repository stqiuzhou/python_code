#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = plot_sms_grid.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/7/16 10:01

"""
    功能：画sms网格图
"""
from fvcom_tools_packages.fvcom_plot import PlotFigure

#%% 数据准备
sms_path = r'E:\fvcom\fvcom_input_file\sms.2dm'

#%% 画图
plot_obj = PlotFigure(grid_path=sms_path,
                      extents=[105, 135, 6, 40], tick_inc=[5, 5])
plot_obj.plot_sms_grid(lw=0.1)
output = r'D:\2018_2019_research\china_sea_1993\images\final\before\grid.svg'
plot_obj.save(output, dpi=300)
plot_obj.show()

