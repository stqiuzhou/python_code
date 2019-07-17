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
from fvcom_tools_packages.fvcom_grid import Grid


class ReadData(Grid):
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
                 variables=None, extents=[0, 360, -90, 90], alti_cycle=None):
        """
        参数
        :param data_path:需要去数据的路径, 可以是str，也可以是list（读取nc的时候）
        :param types: 数据类型
        :param variables: 需要读取的变量名称，部分函数需要，list
        :param extents: 经纬度范围，部分函数需要，例如[lon_left, lon_right, lat_left, lat_right]
        :param str_before: 从多个台风路径中分离出我们所需要的台风，这个是上标，用于read_ch_track
        :param str_after: 从多个台风路径中分离出我们所需要的台风，这个是下标，用于read_ch_track
        :param alti_cycle: 选取高度计的cycle，用于read_alti_data

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
        self.alti_cycle = alti_cycle
        # 分割出文件名
        if isinstance(self.data_path, str):
            self.filename = self.data_path.split('\\')[-1]
        elif isinstance(self.data_path, list):
            self.filenames = list(map(lambda x: x.split('\\')[-1], self.data_path))

        if self.type == 'bwp':
            self.read_bwp_track()
        elif self.type == 'ch':
            self.read_ch_track()
        elif self.type == 'ncep':
            self.read_ncep_data()
        elif self.type == 'ecmwf':
            self.read_ecmwf_data()
        elif self.type == 'fvcom':
            self.read_fvcom_nc()
        elif self.type == 'obc':
            self.read_obc_nc()
        elif self.type == 'alti':
            self.read_alti_data()
        elif self.type == 'site_excel':
            self.read_site_excel()
        elif self.type == 'gauge':
            self.read_gauge_data()

    def read_gauge_data(self):
        """
        功能：读取验潮站的数据
        :return:
        """
        print("读取验潮站数据文件：{}".format(self.filename))
        gauge_data = pd.read_csv(self.data_path, skiprows=[0], header=None,
                                   sep='\s+')
        year = str(gauge_data.iloc[0, 2])[:4]
        gauge_data.drop([0, 1, 2], axis=1, inplace=True)
        level_data = gauge_data.values.flatten()
        time_data = pd.date_range('{}-01-01 00:00:00'.format(year),
                                  '{}-12-31 23:00:00'.format(year),
                                  freq='H')
        time_stamp = pltdate.date2num(time_data)
        setattr(self.data, 'time', time_stamp)
        setattr(self.data, 'elev', level_data)

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
        index_up = ch_data.loc[ch_data[7].isin([self.str_before])].index  # 找出含有'Flo'所在行
        index_down = ch_data.loc[ch_data[7].isin([self.str_after])].index
        select_ch_data = ch_data.iloc[index_up[0]: index_down[0]]
        date = list(map(str, select_ch_data.iloc[1:, 0]))
        ch_date = list(map(lambda x: datetime.strptime(x, '%Y%m%d%H'), date))
        ch_time = pltdate.date2num(ch_date)
        ch_lat = select_ch_data.iloc[1:, 2].values * 0.1  # 转化为numpy
        ch_lon = select_ch_data.iloc[1:, 3].values * 0.1
        ch_press = select_ch_data.iloc[1:, 4].values
        ch_vmax = select_ch_data.iloc[1:, 5].values
        # 存到data中
        setattr(self.data, 'tp_time', ch_time)
        setattr(self.data, 'tp_lat', ch_lat)
        setattr(self.data, 'tp_lon', ch_lon)
        setattr(self.data, 'tp_press', ch_press)
        setattr(self.data, 'tp_vmax', ch_vmax)

    def read_ncep_data(self):
        """
        功能：读取ncep再分析数据
        :return:
        """
        if isinstance(self.data_path, str):
            print("读取NCEP文件：{}".format(self.filename))
            nc_file = Dataset(self.data_path)
        elif isinstance(self.data_path, list):
            # 读取多文件
            print("读取NCEP文件：{}".format(self.filenames))
            nc_file = MFDataset(self.data_path)
            first_file = self.data_path[0].split('\\')[-1]
            end_file = self.data_path[-1].split('\\')[-1]
        else:
            raise ValueError("不支持输入的格式")

        # 读取各种变量，并存储
        # 自己写时间（因为每个ncep文件的时间单位都不一样）
        start_time = first_file.split('.')[2].split('-')[0]
        end_time = end_file.split('.')[2].split('-')[-1] + ' ' + '18:00:00'
        time_range = pd.date_range(start_time, end_time, freq='6h')
        time = pltdate.date2num(time_range)
        setattr(self.data, 'time', time)
        # 选取范围
        lon_temp = nc_file.variables['lon'][:]
        lat_temp = nc_file.variables['lat'][:]
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
        if 'wind' in self.variables:
            u10 = nc_file.variables['U_GRD_L105'][:, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
            setattr(self.data, 'u10', u10)
            v10 = nc_file.variables['V_GRD_L105'][:, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
            setattr(self.data, 'v10', v10)
        if 'slp' in self.variables:
            slp = nc_file.variables['PRES_L1'][:, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
            setattr(self.data, 'slp', slp)

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
            u10 = nc_file.variables['u10'][y, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
            setattr(self.data, 'u10', u10)
            v10 = nc_file.variables['v10'][y, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
            setattr(self.data, 'v10', v10)
        if 'sst' in self.variables:
            sst = nc_file.variables['sst'][y, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
            setattr(self.data, 'sst', sst - 273.15)
        if 't2m' in self.variables:
            t2m = nc_file.variables['t2m'][y, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
            setattr(self.data, 't2m', t2m - 273.15)
        if 'slp' in self.variables:
            slp = nc_file.variables['sp'][y, lat_left_index:lat_right_index + 1,
                  lon_left_index:lon_right_index + 1]
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
        try:
            date = [datetime.strptime(''.join(t.astype(str)), '%Y-%m-%dT%H:%M:%S.%f') for t in time]
        except:
            date = [datetime.strptime(''.join(t.astype(str)), '%Y/%m/%d %H:%M:%S      ') for t in time]
        time_final = pltdate.date2num(date)
        if 'wind' in self.variables:
            u10 = nc_file.variables['uwind_speed'][:]
            v10 = nc_file.variables['vwind_speed'][:]
            setattr(self.data, 'uwnd', u10)
            setattr(self.data, 'vwnd', v10)
        if 'slp' in self.variables:
            slp = nc_file.variables['air_pressure'][:]
            setattr(self.data, 'slp', slp)
        if 'zeta' in self.variables:
            zeta = nc_file.variables['zeta'][:]
            setattr(self.data, 'zeta', zeta)
        if 'h' in self.variables:
            h = nc_file.variables['h'][:]
            setattr(self.data, 'h', h)
        setattr(self, 'lon', lon)
        setattr(self, 'lat', lat)
        setattr(self, 'lonc', lonc)
        setattr(self, 'latc', latc)
        setattr(self, 'nv', nv)
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

    def read_alti_data(self, *args, **kwargs):
        """
        功能：读取高度计数据
        :param *args
        :param **kwargs
        :return:
        """
        print("读取高度计文件：{}".format(self.filename))
        alti_nc = Dataset(self.data_path, *args, **kwargs)
        alti_lat = alti_nc.variables['lat'][:]
        alti_lon = alti_nc.variables['lon'][:]
        alti_cycle = alti_nc.variables['cycle'][:]
        alti_time = alti_nc.variables['time'][:]
        alti_time_tmp = num2date(alti_time, alti_nc.variables['time'].units)
        alti_time = pltdate.date2num(alti_time_tmp)
        alti_sla = alti_nc.variables['sla'][:]
        alti_dac = alti_nc.variables['dac'][:]
        alti_sla = alti_sla + alti_dac
        if self.alti_cycle is not None:
            if isinstance(self.alti_cycle, int):
                index = np.where(alti_cycle == self.alti_cycle)
                alti_sla = alti_sla[:, index].ravel()
                alti_time = alti_time[:, index].ravel()
            else:
                alti_sla_final = np.ma.ones([len(alti_lon), len(self.alti_cycle)])
                alti_time_final = np.ma.ones([len(alti_lon), len(self.alti_cycle)])
                for idx, icycle in enumerate(self.alti_cycle):
                    index = np.where(alti_cycle == icycle)[0][0]
                    alti_sla_tmp = alti_sla[:, index].ravel()
                    alti_time_tmp = alti_time[:, index].ravel()
                    alti_sla_final[:, idx] = alti_sla_tmp
                    alti_time_final[:, idx] = alti_time_tmp
                alti_sla = alti_sla_final
                alti_time = alti_time_final
            alti_cycle = self.alti_cycle
        setattr(self.data, 'alti_lat', alti_lat)
        setattr(self.data, 'alti_lon', alti_lon)
        setattr(self.data, 'alti_time', alti_time)
        setattr(self.data, 'alti_sla', alti_sla)
        setattr(self.data, 'alti_cycle', alti_cycle)

    def read_site_excel(self, *args, **kwargs):
        """
        功能：读取实测数据，包括风场，温度和气压
        :param args:
        :param kwargs:
        :return:
        """
        print('读取实测数据文件：{}'.format(self.filename))
        site_data = pd.read_excel(self.data_path, sheet_name='wind', *args, **kwargs)
        station = self.data_path.split('\\')[-1][0:-5]
        time_str = site_data['time'].astype(str)
        time = [datetime.strptime(x, '%Y%m%d%H') for x in time_str]
        time_stamp = pltdate.date2num(time)
        if 'wind' in self.variables:
            site_data = pd.read_excel(self.data_path, sheet_name='wind')
            wind_spd = site_data['wind_spd'].to_numpy()
            wind_dir = site_data['wind_dir'].to_numpy()
            setattr(self.data, 'wind_spd', wind_spd)
            setattr(self.data, 'wind_dir', wind_dir)
        if 'temp' in self.variables:
            site_data = pd.read_excel(self.data_path, sheet_name='temp')
            temp = site_data['temp'].to_numpy()
            max_temp = site_data['max_temp'].to_numpy()
            min_temp = site_data['min_temp'].to_numpy()
            setattr(self.data, 'temp', temp)
            setattr(self.data, 'max_temp', max_temp)
            setattr(self.data, 'min_temp', min_temp)
        if 'pressure' in self.variables:
            site_data = pd.read_excel(self.data_path, sheet_name='pressure')
            pressure = site_data['pressure'].to_numpy()
            max_pressure = site_data['max_pressure'].to_numpy()
            min_pressure = site_data['min_pressure'].to_numpy()
            setattr(self.data, 'pressure', pressure)
            setattr(self.data, 'max_pressure', max_pressure)
            setattr(self.data, 'min_pressure', min_pressure)
        setattr(self.data, 'station', station)
        setattr(self.data, 'time', time_stamp)
