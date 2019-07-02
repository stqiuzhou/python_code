#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = fvcom_prep.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/5 21:47

import numpy as np
from netCDF4 import Dataset, date2num
from .fvcom_grid import Grid
from .utily import PassiveStore
from datetime import datetime
from scipy.interpolate import griddata, interp1d

class FvcomPrep(Grid):

    def __init__(self, data_path=None, **kwargs):
        if data_path is not None:
            super().__init__(data_path)

    def interp_temp_spatial(self, perp_lon, perp_lat, perp_time, perp_value,
                            interp_lon, interp_lat, interp_time, time_single=False):
        """
        对时空方向分别进行插值
        :param perp_data: 插值所用的数据，包括lon，lat，time，values
        :param interp_data: 待插值的数据，包括lon，lat，time
        :return: interped_data: 插值结果
        """
        # 先对空间进行插值
        X, Y = np.meshgrid(perp_lon, perp_lat)
        perp_time_num = len(perp_time)
        interp_spatial_num = len(interp_lon)
        interped_data_time = np.ones([perp_time_num, interp_spatial_num])
        for itime in range(perp_time_num):
            interped_tmp = griddata((X.ravel(), Y.ravel()), perp_value[itime, :, :].ravel(),
                                    (interp_lon, interp_lat))
            interped_data_time[itime, :] = interped_tmp
        # 再对时间进行插值
        if time_single:
            interped_data = np.ones(interp_spatial_num)
        else:
            interped_data = np.ones([len(interp_time), interp_spatial_num])
        for ilon in range(interp_spatial_num):
            func = interp1d(perp_time, interped_data_time[:, ilon])
            if time_single:
                interped_tmp = func(interp_time[ilon])
                interped_data[ilon] = interped_tmp
            else:
                interped_tmp = func(interp_time)
                interped_data[:, ilon] = interped_tmp
        return interped_data

    def interp_surface_forcing(self, data):
        """
        功能：插值表面强迫数据
        :param data: 一个数据类，包含u10, v10, slp等
        :return:
        """
        print("正在进行插值……")
        t_start = datetime.now()
        forcing_data = PassiveStore()
        time_length = len(data.time)
        uwnd_final = np.zeros([time_length, self.nele], dtype='f')
        vwnd_final = np.zeros([time_length, self.nele], dtype='f')
        slp_final = np.zeros([time_length, self.node], dtype='f')
        for i in range(time_length):
            LON, LAT = np.meshgrid(data.lon, data.lat)
            if 'u10' in data:
                uwind_tmp = griddata((LON.ravel(), LAT.ravel()), data.u10[i, :, :].ravel(),
                                     (self.lonc, self.latc))
                if len(np.argwhere(np.isnan(uwind_tmp))) > 0:
                    raise ValueError('存在NAN值')
                uwnd_final[i, :] = uwind_tmp
            if 'v10' in data:
                vwind_tmp = griddata((LON.ravel(), LAT.ravel()), data.v10[i, :, :].ravel(),
                                     (self.lonc, self.latc))
                if len(np.argwhere(np.isnan(vwind_tmp))) > 0:
                    raise ValueError('存在NAN值')
                vwnd_final[i, :] = vwind_tmp
            if 'slp' in data:
                slf_tmp = griddata((LON.ravel(), LAT.ravel()), data.slp[i, :, :].ravel(),
                                   (self.lon, self.lat))
                if len(np.argwhere(np.isnan(slf_tmp))) > 0:
                    raise ValueError('存在NAN值')
                slp_final[i, :] = slf_tmp
        setattr(forcing_data, 'uwnd', uwnd_final)
        setattr(forcing_data, 'vwnd', vwnd_final)
        setattr(forcing_data, 'slp', slp_final)
        t_end = datetime.now()
        print("插值共花了{:d}秒".format((t_end-t_start).seconds))
        return forcing_data

    def write_obc_nc(self, ncfile, ptime, zeta, *args, **kwargs):
        """
        功能：将obc数据写入到nc文件中
        :param ncfile: 输出文件名
        :param ptime: 时间变量，格式为datetime
        :param obc_data: obc数据
        :param args:
        :param kwargs:
        :return:
        """
        globals = {'type': 'FVCOM TIME SERIES ELEVATION FORCING FILE',
                   'title': 'JULIAN FVCOM TIDAL FORCING DATA CREATED FROM OLD FILE TYPE: anything',
                   'history': "File created using {} with write_obc_nc from python".format(
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        # 定义维度
        dims = {'nobc': self.obc, 'time': 0, 'DateStrLen': 26}

        with WriteForcing(ncfile, dims, globle_attributes=globals, format='NETCDF3_64BIT') as obc_ncfile:
            atts = {'long_name': 'Open Boundary Node Number', 'grid': 'obc_grid'}
            obc_ncfile.add_variable('obc_nodes', self.open_boundary_nodes + 1, ['nobc'],
                                    attributes=atts, format='i')
            # 写入时间
            obc_ncfile.write_fvcom_time(ptime)
            atts = {'long_name': 'Open Boundary Elevation', 'units': 'meters'}
            obc_ncfile.add_variable('elevation', zeta, ['time', 'nobc'],
                                    attributes=atts)


    def write_surface_forcing(self, ncfile, ptime, forcing_data, **kwargs):
        """
        功能：将表面强迫数据写入nc文件，数据经常来自ncep、ecmwf
        :param ncfile: 输出nc文件
        :param ptime:  时间变量，格式为datetime
        :param forcing_data: 表面驱动数据
        :param kwargs:
        :return:
        """
        # 定义全局变量
        globals = {'type': "FVCOM Surface Forcing input DATA VERSION :",
                   'title': "FVCOM Grid Forcing Data file",
                   'institution': "State Key Laboratory of Satellite Ocean Environment Dynamics, SIO",
                   'source': "FVCOM grid (unstructured) surface forcing",
                   'history': "File created using {} with write_surface_forcing from python".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                   'filename': str(ncfile),
                   'references': "http://fvcom.smast.umassd.edu, http://codfish.smast.umassd.edu",
                   'Conventions': "CF-1.0"}
        # 定义维度
        dims = {'nele': self.nele, 'node': self.node, 'three': 3,
                'time': 0, 'DateStrLen': 26, 'scalar': 1}

        with WriteForcing(ncfile, dims, globle_attributes=globals, format='NETCDF3_64BIT') as surf_ncfile:
            # 写入网格
            print('写入网格中……')
            grid = Grid(self.grid_path)
            surf_ncfile.write_fvcom_grid(grid)
            # 写入时间
            print('写入时间中……')
            surf_ncfile.write_fvcom_time(ptime)
            # 写入表明强迫数据
            if 'uwnd' in forcing_data:
                atts = {'long_name': 'Eastward Wind Speed',
                        'standard_name': 'Wind Speed',
                        'units': 'm/s',
                        'gird': 'fvcom_grid',
                        'type': 'data'}
                surf_ncfile.add_variable('uwind_speed', forcing_data.uwnd, ['time', 'nele'],
                                         attributes=atts)
            if 'vwnd' in forcing_data:
                atts = {'long_name': 'Northward Wind Speed',
                        'standard_name': 'Wind Speed',
                        'units': 'm/s',
                        'gird': 'fvcom_grid',
                        'type': 'data'}
                surf_ncfile.add_variable('vwind_speed', forcing_data.vwnd, ['time', 'nele'],
                                         attributes=atts)
            if 'slp' in forcing_data:
                atts = {'long_name': 'Surface air pressure',
                        'units': 'Pa',
                        'gird': 'fvcom_grid',
                        'coordinate': self.nativeCoords,
                        'type': 'data'}
                surf_ncfile.add_variable('air_pressure', forcing_data.slp, ['time', 'node'],
                                         attributes=atts)


class WriteForcing(object):
    """
    功能：创建nc文件，用于写入FVCOM输入文件
    """

    def __init__(self, filename, dimensions, globle_attributes, **kwargs):
        """
        参数
        :param filename: 输出的nc文件名（加路径）
        :param dimensions: nc文件的dimensions
        :param globle_attributes: nc文件的globle attributes
        :param kwargs:
        """
        self.nc = Dataset(filename, 'w', **kwargs)

        for dimension in dimensions:
            self.nc.createDimension(dimension, dimensions[dimension])

        if globle_attributes:
            for attribute in globle_attributes:
                setattr(self.nc, attribute, globle_attributes[attribute])

    def add_variable(self, name, data, dimensions, attributes=None, format='f4'):
        """
        功能： 添加变量到nc文件中
        :param name: 变量名
        :param data: 变量值
        :param dimensions: 变量维度
        :param attributes: 变量属性
        :param format:     变量数据格式
        :param ncopts:  dict的option可以被用于创建变量
        :return:
        """
        if isinstance(dimensions, list):
            dimensions = tuple(dimensions)
        var = self.nc.createVariable(name, format, dimensions)
        if attributes:
            for attribute in attributes:
                setattr(var, attribute, attributes[attribute])

        var[:] = data
        # setattr(self, name, var)

    def write_fvcom_time(self, time, **kwargs):
        """
        功能：写入fvcom时间到nc文件中
        :param time: 时间变量，datetime格式
        :param kwargs:
        :return:
        """
        print('正在写入时间……')
        time = [x.replace(tzinfo=None) for x in time]
        mjd = date2num(time, units='days since 1858-11-17 00:00:00')
        Itime = np.floor(mjd)  # Julian day的整数部分
        Itime2 = (mjd - Itime) * 24 * 60 * 60 * 1000  # 从0点开始的毫秒数
        Times = [t.strftime('%Y-%m-%dT%H:%M:%S.%f') for t in time]

        # nprocs
        atts = {'long_name': 'number of processors'}
        self.add_variable('nprocs', 1, ['scalar'], attributes=atts, format='i')
        # iint
        atts = {'long_name': 'internal mode iteration number'}
        self.add_variable('iint', np.arange(len(time)), ['time'], attributes=atts, format='i')
        # time
        atts = {'long_name': 'time',
                'units': 'days since 1858-11-17 00:00:00',
                'format': 'modified julian day (MJD)',
                'time_zone': 'UTC'}
        self.add_variable('time', mjd, ['time'], attributes=atts, format='f')
        # Itime
        atts = {'units': 'days since 1858-11-17 00:00:00',
                'format': 'modified julian day (MJD)',
                'time_zone': 'UTC'}
        self.add_variable('Itime', Itime, ['time'], attributes=atts, format='i')
        # Itime2
        atts = {'units': 'msec since 00:00:00',
                'time_zone': 'UTC',
                'long_name': 'time'}
        self.add_variable('Itime2', Itime2, ['time'], attributes=atts, format='i')
        # Times
        atts = {'long_name': 'Calendar Date',
                'format': 'String: Calendar Time',
                'time_zone': 'UTC'}
        self.add_variable('Times', Times, ['time', 'DateStrLen'], format='c', attributes=atts)

    def write_fvcom_grid(self, grid, native_coordinates='spherical', **kwargs):
        """
        功能：写入网格数据到nc文件中
        :param grid: 包含网格数据的一个类，包括'x', 'y', 'xc', 'yc'，'lat', 'lon', 'latc', 'lonc','nv'
        :param native_coordinates: 坐标轴选择，默认为spherical
        :param kwargs:
        :return:
        """
        print('正在写入网格数据……')
        if native_coordinates == 'spherical':
            for iname in ['lat', 'lon', 'latc', 'lonc','nv']:
                if iname == 'lat':
                    atts = {'long_name': 'longitude',
                            'units': 'degrees_east'}
                    self.add_variable('lon', grid.lon, ['node'], format='f',attributes=atts)
                if iname == 'lon':
                    atts = {'long_name': 'latitude',
                            'units': 'degrees_north'}
                    self.add_variable('lat', grid.lat, ['node'], format='f',attributes=atts)
                if iname == 'lonc':
                    atts = {'long_name': 'zonal longitude',
                            'units': 'degrees_east'}
                    self.add_variable('lonc', grid.lonc, ['nele'], format='f', attributes=atts)
                if iname == 'latc':
                    atts = {'long_name': 'zonal latitude',
                            'units': 'degrees_north'}
                    self.add_variable('latc', grid.latc, ['nele'], format='f', attributes=atts)
                if iname == 'nv':
                    atts = {'long_name': 'nodes surrounding element'}
                    # nv is is (three,nele), while mesh.nv is (nele,3)，should transpose it
                    self.add_variable('nv', np.transpose(grid.nv), ['three', 'nele'], format='i', attributes=atts)
        elif native_coordinates == 'cartesian':
            for iname in ['x', 'y', 'xc', 'yc','nv']:
                if iname == 'x':
                    atts = {'long_name': 'nodal x-coordinate',
                            'units': 'meters'}
                    self.add_variable('x', grid.x, ['node'], format='f',attributes=atts)
                if iname == 'y':
                    atts = {'long_name': 'nodal y-coordinate',
                            'units': 'meter'}
                    self.add_variable('y', grid.y, ['node'], format='f',attributes=atts)
                if iname == 'xc':
                    atts = {'long_name': 'zonal x-coordinate',
                            'units': 'meters'}
                    self.add_variable('xc', grid.xc, ['nele'], format='f', attributes=atts)
                if iname == 'yc':
                    atts = {'long_name': 'zonal y-coordinate',
                            'units': 'meters'}
                    self.add_variable('yc', grid.yc, ['nele'], format='f', attributes=atts)
                if iname == 'nv':
                    atts = {'long_name': 'nodes surrounding element'}
                    # nv is is (three,nele), while mesh.nv is (nele,3)，should transpose it
                    self.add_variable('nv', np.transpose(grid.nv), ['three', 'nele'], format='f', attributes=atts)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.nc.close()






