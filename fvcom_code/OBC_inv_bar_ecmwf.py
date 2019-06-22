#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = OBC_inverse_barometric_adjuested.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/21 14:21

from fvcom_tools_packages.fvcom_prep import FvcomPrep
from fvcom_tools_packages.read_data import ReadData
from fvcom_tools_packages.fvcom_grid import Grid
import numpy as np
from scipy.interpolate import interp1d, griddata
import os
from matplotlib.dates import num2date
# ecmwf数据准备
ecmwf_slp_dir = r'E:\ecmwf\press\1993'
ecmwf_slp_files = os.listdir(ecmwf_slp_dir)
select_ecmwf_slp_path = [os.path.join(ecmwf_slp_dir, x) for x in ecmwf_slp_files[7:10]]
ecmwf_slp_data = ReadData(select_ecmwf_slp_path, types='ecmwf',
                          variables=['lon', 'lat', 'time', 'slp'],
                          extents=[105, 135, 5, 40])
# obc文件
obc_nc_path = r'H:\fvcom\fvcom_input_file\julian_obc_all.nc'
obc_data = ReadData(obc_nc_path, types='obc',
                    variables=['obc', 'elev'])
obc_num = len(obc_data.data.obc)
# 网格文件
sms_path = r'H:\fvcom\fvcom_input_file\sms.2dm'
sms_data = Grid(sms_path)
# obc的经纬度
obc_lat = sms_data.lat[0:obc_num]
obc_lon = sms_data.lon[0:obc_num]

# 气压空间方向插值
LON, LAT = np.meshgrid(ecmwf_slp_data.data.lon, ecmwf_slp_data.data.lat)
pressure_time_obc = np.ones([len(ecmwf_slp_data.data.time), obc_num], dtype='f')
for itime in range(len(ecmwf_slp_data.data.time)):
    interped_obc_tmp = griddata((LON.ravel(), LAT.ravel()), ecmwf_slp_data.data.slp[itime, :, :].ravel(),
                        (obc_lon, obc_lat), method='nearest')
    pressure_time_obc[itime, :] = interped_obc_tmp

# 气压时间方向插值
pressure_obc = np.ones([len(obc_data.data.time), obc_num])
for iobc in range(obc_num):
    func = interp1d(ecmwf_slp_data.data.time, pressure_time_obc[:, iobc])
    pressure_obc_tmp = func(obc_data.data.time)
    pressure_obc[:, iobc] = pressure_obc_tmp

IB = -9.948 * (pressure_obc - 101325) * 0.01  # 单位 mm
elevation = obc_data.data.elev + IB * 0.001

# 写入到nc文件中
prep = FvcomPrep(sms_path)
output_ncfile = r'H:\fvcom\fvcom_input_file\julian_obc_adjuested1.nc'
ptime = num2date(obc_data.data.time)
prep.write_obc_nc(output_ncfile, ptime, elevation)
