#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = fvcom_post.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/23 19:22

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_plot import PlotFigure
import pandas as pd
import numpy as np
from matplotlib.dates import date2num


class FvcomPost(object):

    def __init__(self, tide_path=None, wind_path=None):
        self.tide_path = tide_path
        self.wind_path = wind_path

    def calculate_model_zeta(self, station, start_time, end_time, figure=True, *args, **kwargs):
        wind_zeta_data = ReadData(self.wind_path, types='fvcom',
                                   variables=['time', 'zeta'])
        tide_zeta_data = ReadData(self.tide_path, types='fvcom',
                                   variables=['time', 'zeta'])
        index = wind_zeta_data.find_nearest_point('zeta', station)
        time_range = pd.date_range(start_time, end_time, freq='H')
        time_stamp = date2num(time_range)
        start_index = np.where(wind_zeta_data.data.time[:] == time_stamp[0])
        end_index = np.where(wind_zeta_data.data.time[:] == time_stamp[-1])
        zeta_wind = wind_zeta_data.data.zeta[start_index[0][0]: end_index[0][0]+1, index] - \
                    tide_zeta_data.data.zeta[start_index[0][0]:end_index[0][0]+1, index]
        if figure:
            zeta_fig = PlotFigure(cartesian=True)
            zeta_fig.plot_lines(time_stamp, zeta_wind, time_series=True, *args, **kwargs)
        return zeta_wind
