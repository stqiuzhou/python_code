#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = write_surf_forcing_from_ecmwf.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/17 14:40

from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_prep import FvcomPrep
from fvcom_tools_packages.utily import PassiveStore
import os
import matplotlib.dates as pltdate
"""
    功能：表面强迫的nc输入，包括风场和气压场，数据来源ECMWF。
"""
# 列出需要读取ecmwf数据的路径
ecmwf_wind_dir = r'E:\ecmwf\wind\1993'
ecmwf_wind_files = os.listdir(ecmwf_wind_dir)
select_ecmwf_wind_path = [os.path.join(ecmwf_wind_dir, x) for x in ecmwf_wind_files[7:10]]

ecmwf_slp_dir = r'E:\ecmwf\press\1993'
ecmwf_slp_files = os.listdir(ecmwf_slp_dir)
select_ecmwf_slp_path = [os.path.join(ecmwf_slp_dir, x) for x in ecmwf_slp_files[7:10]]

# 读取数据
ecmwf_wind_data = ReadData(select_ecmwf_wind_path, types='ecmwf',
                      variables=['lon','lat', 'time', 'wind'],
                      extents=[5, 40, 105, 135])
ecmwf_slp_data = ReadData(select_ecmwf_slp_path, types='ecmwf',
                          variables=['time', 'slp'],
                          extents=[5, 40, 105, 135])
ecmwf_data = PassiveStore()
setattr(ecmwf_data, 'lon', ecmwf_wind_data.data.lon)
setattr(ecmwf_data, 'lat', ecmwf_wind_data.data.lat)
setattr(ecmwf_data, 'time', ecmwf_wind_data.data.time)
setattr(ecmwf_data, 'u10', ecmwf_wind_data.data.u10)
setattr(ecmwf_data, 'v10', ecmwf_wind_data.data.v10)
setattr(ecmwf_data, 'slp', ecmwf_slp_data.data.slp)
ptime = pltdate.num2date(ecmwf_data.time, tz=None)

# 网格数据路径
grid_path = r'H:\fvcom\fvcom_input_file\sms.2dm'
# 表面强迫的nc输出
prep = FvcomPrep(grid_path)
interped_data = prep.interp_surface_forcing(ecmwf_data)
prep.write_surface_forcing(r'H:\fvcom\fvcom_input_file\ecmwf_08_10.nc',
                           ptime, interped_data)

