#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = read_data.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/3 22:06

import os
from netCDF4 import Dataset, MFDataset, num2date
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.dates as pltdate
from .utily import PassiveStore


class ReadData(object):
    """
    功能：读取各种类型的数据
    方法：
    1. read_tp_track —— 读取JTWC发布的台风最佳路径
    2. read_ch_track —— 读取中国气象局发布的台风最佳路径
    3. read_ecmwf_data —— 读取ecmwf数据
    4. read_fvcom_nc —— 读取包含网格数据的fvcom nc文件
    5. read_obc_nc —— 读取边界点的nc文件
    """

    def __init__(self, data_path, types=None, str_before=None, str_after=None,
                 variables=None, extents=[0, 360, -90, 90]):
        """
        参数
        :param data_path:需要去数据的路径, 可以是str，也可以是list（读取nc的时候）
        :param types: 数据类型
        :param variables: 需要读取的变量名称，部分函数需要，list
        :param extents: 经纬度范围，部分函数需要，例如[lon_left, lon_right, lat_left, lat_right]

        返回
        ：:return self.data
        """
        self.data_path = data_path
        self.str_before = str_before
        self.str_after = str_after
        self.variables = variables
        self.data = PassiveStore()
        self.type = types
        self.extents = extents
        # 分割出文件名
        if isinstance(self.data_path, str):
            self.filename = self.data_path.split('\\')[-1]
        elif isinstance(self.data_path, list):
            self.filenames = list(map(lambda x: x.split('\\')[-1], self.data_path))

        if self.type == 'bwp':
            self.read_bwp_track()
        elif self.type == 'ch':
            self.read_ch_track()
        elif self.type == 'ecmwf':
            self.read_ecmwf_data()
        elif self.type == 'fvcom':
            self.read_fvcom_nc()
        elif self.type == 'obc':
            self.read_obc_nc()

    def read_bwp_track(self):
        """
        功能：读取JTWC发布的台风最佳路径
        网站：https://www.metoc.navy.mil/jtwc/jtwc.html
        返回：
        :return: self.data

        """
        print("读取JTWC台风最佳路径文件：{}".format(self.filename))
        tp_data = pd.read_csv(self.data_path, sep=',',
                              usecols=[2, 6, 7, 8],
                              names=['date', 'lat(0.1degree)',
                                     'lon(0.1degree)', 'vmax(knots)'])
        date = list(map(str, tp_data['date']))
        tp_date = list(map(lambda x: datetime.strptime(x, '%Y%m%d%H'), date))
        tp_time = pltdate.date2num(tp_date)
        tp_vmax = tp_data['vmax(knots)']
        # fromiter 从迭代对象中建立数组对象
        tp_lon = np.fromiter(map(lambda x: x[0:-1], tp_data['lon(0.1degree)']),
                             dtype=int) * 0.1
        tp_lat = np.fromiter(map(lambda x: x[0:-1], tp_data['lat(0.1degree)']),
                             dtype=int) * 0.1
        # 存到data中
        setattr(self.data, 'tp_time', tp_time)
        setattr(self.data, 'tp_lon', tp_lon)
        setattr(self.data, 'tp_lat', tp_lat)
        setattr(self.data, 'tp_vmax', tp_vmax)

    def read_ch_track(self):
        """
        功能：读取中国气象局发布的台风最佳路径
        网站：http://tcdata.typhoon.org.cn/
        返回：
        :return: self.data
        """
        print("读取CH台风最佳路径文件：{}".format(self.filename))
        ch_data = pd.read_csv(self.data_path, sep='\s+',
                              header=None)
        index_up = ch_data.loc[ch_data[7].isin([self.str_before])].index      # 找出含有'Flo'所在行
        index_down = ch_data.loc[ch_data[7].isin([self.str_after])].index
        select_ch_data = ch_data.iloc[index_up[0]: index_down[0]]
        date = list(map(str, select_ch_data.iloc[1:, 0]))
        ch_date = list(map(lambda x: datetime.strptime(x, '%Y%m%d%H'), date))
        ch_time = pltdate.date2num(ch_date)
        ch_lat = select_ch_data.iloc[1:, 2].values * 0.1      # 转化为numpy
        ch_lon = select_ch_data.iloc[1:, 3].values * 0.1
        ch_press = select_ch_data.iloc[1:, 4].values
        ch_vmax = select_ch_data.iloc[1:, 5].values
        # 存到data中
        setattr(self.data, 'tp_time', ch_time)
        setattr(self.data, 'tp_lat', ch_lat)
        setattr(self.data, 'tp_lon', ch_lon)
        setattr(self.data, 'tp_press', ch_press)
        setattr(self.data, 'tp_vmax', ch_vmax)

    def read_ecmwf_data(self):
        """
        功能：读取ecmwf数据
        返回
        :return: self.data
        """
        if isinstance(self.data_path, str):
            print("读取ECMWF文件：{}".format(self.filename))
            nc_file = Dataset(self.data_path)
        elif isinstance(self.data_path, list):
            # 读取多文件
            print("读取ecmwf文件：{}".format(self.filenames))
            nc_file = MFDataset(self.data_path)
        else:
            raise ValueError("不支持输入的格式")

        # 读取各种变量，并存储
        # 选取范围
        lon_temp = nc_file.variables['longitude'][:]
        lat_temp = nc_file.variables['latitude'][:]
        lat_left_index = np.where(lat_temp <= self.extents[3])[0][0]
        lat_right_index = np.where(lat_temp >= self.extents[2])[0][-1]
        lon_left_index = np.where(lon_temp >= self.extents[0])[0][0]
        lon_right_index = np.where(lon_temp <= self.extents[1])[0][-1]
        lat = lat_temp[lat_left_index:lat_right_index + 1]
        lon = lon_temp[lon_left_index:lon_right_index + 1]
        if 'lon' in self.variables:
            setattr(self.data, 'lon', lon)
        if 'lat' in self.variables:
            setattr(self.data, 'lat', lat)
        if 'time' in self.variables:
            time_temp = nc_file.variables['time'][:]
            time_date = num2date(time_temp, nc_file.variables['time'].units)
            time = pltdate.date2num(time_date)
            x, y = np.unique(time, return_index=True)
            setattr(self.data, 'time', x)
        if 'wind' in self.variables:
            u10 = nc_file.variables['u10'][y, lat_left_index:lat_right_index+1,
                  lon_left_index:lon_right_index+1]
            setattr(self.data, 'u10', u10)
            v10 = nc_file.variables['v10'][y, lat_left_index:lat_right_index+1,
                  lon_left_index:lon_right_index+1]
            setattr(self.data, 'v10', v10)
        if 'sst' in self.variables:
            sst = nc_file.variables['sst'][y, lat_left_index:lat_right_index+1,
                  lon_left_index:lon_right_index+1]
            setattr(self.data, 'sst', sst)
        if 't2m' in self.variables:
            t2m = nc_file.variables['t2m'][y, lat_left_index:lat_right_index+1,
                  lon_left_index:lon_right_index+1]
            setattr(self.data, 't2m', t2m)
        if 'slp' in self.variables:
            slp = nc_file.variables['sp'][y, lat_left_index:lat_right_index+1,
                  lon_left_index:lon_right_index+1]
            setattr(self.data, 'slp', slp)

    def read_fvcom_nc(self, mode='r', *args, **kwargs):
        """
        功能：读取fvcom的nc文件
        :return:
        """
        print("读取fvcom的nc文件：{}".format(self.filename))
        nc_file = Dataset(self.data_path, mode, *args, **kwargs)
        lon = nc_file.variables['lon'][:]
        lat = nc_file.variables['lat'][:]
        lonc = nc_file.variables['lonc'][:]
        latc = nc_file.variables['latc'][:]
        nv = nc_file.variables['nv'][:]
        time = nc_file.variables['Times'][:]
        date = [datetime.strptime(''.join(t.astype(str)), '%Y-%m-%dT%H:%M:%S.%f') for t in time]
        time_final = pltdate.date2num(date)
        if 'wind' in self.variables:
            u10 = nc_file.variables['uwind_speed'][:]
            v10 = nc_file.variables['vwind_speed'][:]
            setattr(self.data, 'uwnd', u10)
            setattr(self.data, 'vwnd', v10)
        if 'slp' in self.variables:
            slp = nc_file.variables['air_pressure'][:]
            setattr(self.data, 'slp', slp)
        setattr(self.data, 'lon', lon)
        setattr(self.data, 'lat', lat)
        setattr(self.data, 'lonc', lonc)
        setattr(self.data, 'latc', latc)
        setattr(self.data, 'nv', nv)
        setattr(self.data, 'time', time_final)

    def read_obc_nc(self, *args, **kwargs):
        """
        功能：读取obc的nc文件
        :param args:
        :param kwargs:
        :return:
        """
        print("读取边界点的nc文件：{}".format(self.filename))
        nc_file = Dataset(self.data_path, *args, **kwargs)
        time = nc_file.variables['Times'][:]
        date = [datetime.strptime(''.join(t.astype(str)), '%Y-%m-%dT%H:%M:%S.%f') for t in time]
        time_final = pltdate.date2num(date)
        setattr(self.data, 'time', time_final)
        if 'obc' in self.variables:
            obc = nc_file.variables['obc_nodes'][:]
            setattr(self.data, 'obc', obc)
        if 'elev' in self.variables:
            elev = nc_file.variables['elevation'][:]
            setattr(self.data, 'elev', elev)
