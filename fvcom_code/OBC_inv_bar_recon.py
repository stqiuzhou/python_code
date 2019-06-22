#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = OBC_inverse_barometric_adjuested.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/21 14:21

from fvcom_tools_packages.fvcom_prep import FvcomPrep
from fvcom_tools_packages.read_data import ReadData
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.dates import num2date

# 重构气压场数据准备
recon_press_path = r'H:\fvcom\fvcom_input_file\ecmwf_08_10_rec1.nc'
recon_press_data = ReadData(recon_press_path, types='fvcom',
                            variables=['slp'])

# obc文件
obc_nc_path = r'H:\fvcom\fvcom_input_file\julian_obc_all.nc'
obc_data = ReadData(obc_nc_path, types='obc',
                    variables=['obc', 'elev'])
obc_num = len(obc_data.data.obc)

# obc的经纬度
obc_lat = recon_press_data.data.lat[0:obc_num]
obc_lon = recon_press_data.data.lon[0:obc_num]
obc_press = recon_press_data.data.slp[:, 0:obc_num]

# 气压时间方向插值
pressure_obc = np.ones([len(obc_data.data.time), obc_num])
for iobc in range(obc_num):
    func = interp1d(recon_press_data.data.time, obc_press[:, iobc])
    pressure_obc_tmp = func(obc_data.data.time)
    pressure_obc[:, iobc] = pressure_obc_tmp

IB = -9.948 * (pressure_obc - 101325) * 0.01  # 单位 mm
elevation = obc_data.data.elev + IB * 0.001

# 写入到nc文件中
sms_path = r'H:\fvcom\fvcom_input_file\sms.2dm'
prep = FvcomPrep(sms_path)
output_ncfile = r'H:\fvcom\fvcom_input_file\julian_obc_adjusted_recon.nc'
ptime = num2date(obc_data.data.time)
prep.write_obc_nc(output_ncfile, ptime, elevation)
