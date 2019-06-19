#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = model_plot.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/3 22:04

import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from cmocean import cm
import logging
from PyFVCOM.grid import Domain

logger = logging.getLogger(__name__)


class PlotFigure(object):
    """
    功能：画各种类型的图
    方法：
    1. plot_lines —— 画折线图
    """
    def __init__(self, figure=None, axes=None, figsize=(12, 8),
                 extents=None, title=None, title_font=None, ax_font=None,
                 m=None, cartesian=False, tick_inc=None, grid=False,
                 depth=False, cb_label=None):
        """
        参数：
        # :param data: 数据，支持ReadData格式或者Dataset格式
        :param figure: matplotlib 的figure对象
        :param axes:   matplotlib 的 axes对象
        :param figsize: figure的大小
        :param extents:  四元素numpy数组，分别代表横坐标和纵坐标。例如[105, 135, 10, 30]
        :param title:   figure的标题
        :param title_font:  标题的字体，传入的是dict
        :param ax_font:   坐标的字体，传入的是dict
        :param m:       Basemap对象
        :param cartesian:   True表示简单的笛卡尔坐标系，False表示basemap
        :param tick_inc:    坐标轴的刻度，二元素数组，分别表示x，y
        :param grid:    坐标轴网格，True表示有网格，False表示没网格
        :param depth:   True表示添加水深数据，False表示不添加水深数据
        :param cb_label: colorbar 的标签
        """
        # self.ds = data
        self.fig = figure
        self.ax = axes
        self.figsize = figsize
        self.extents = extents
        self.title = title
        self.title_font = title_font
        self.axes_font = ax_font
        self.m = m
        self.cartesian = cartesian
        self.tick_inc = tick_inc
        self.grid = grid
        self.depth = depth
        self.cb_label = cb_label

        # 判断是否需要网格 0代表无网格
        if self.grid:
            self.lw = 0.5
        else:
            self.lw = 0

        # # 判断数据是ReadData格式还是Dataset格式
        # if isinstance(self.ds, ReadData):
        #     self._ReadData = True
        # else:
        #     self._ReadData = False
        self._init_figure()

    def _init_figure(self):
        # 初始化图像
        if self.fig is None:
            self.fig = plt.figure(figsize=self.figsize)
        if self.ax is None:
            # 四个参数为坐下宽高相对整体figure的大小
            self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        if self.title:
            self.ax.set_title(self.title, fontdict=self.title_font, pad=15)
        # basemap
        if not self.cartesian:
            if self.m is None:
                # 添加basemap
                self.m = Basemap(projection='mill',
                                 lat_0=np.mean(self.extents[-2:]),
                                 lon_0=np.mean(self.extents[:2]),
                                 llcrnrlon=np.min(self.extents[:2]),
                                 llcrnrlat=np.min(self.extents[-2:]),
                                 urcrnrlon=np.max(self.extents[:2]),
                                 urcrnrlat=np.max(self.extents[-2:]),
                                 resolution='l', ax=self.ax)
                # # 使用shapefile精细化海岸线（注意：下面的只有中国和台湾的shapefile）
                # self.m.readshapefile(r'H:\shapefiles\CHN_adm_shp\CHN_adm1',
                #                      'states', drawbounds=True)
                # self.m.readshapefile(r'H:\shapefiles\TWN_adm/TWN_adm1',
                #                      'taiwan')
            # 检查tick_inc间隔是否超过extents
            if self.tick_inc is not None:
                if self.tick_inc[0] > self.extents[1] - self.extents[0]:
                    logger.info('The x-axis tick interval is larger than the plot x-axis extent.')
                if self.tick_inc[1] > self.extents[3] - self.extents[2]:
                    logger.info('The y-axis tick interval is larger than the plot y-axis extent.')
                # 添加坐标轴的经纬度
                meridians = np.arange(np.floor(np.min(self.extents[:2])), np.ceil(np.max(self.extents[:2])),
                                      self.tick_inc[0])
                parallels = np.arange(np.floor(np.min(self.extents[2:])), np.ceil(np.max(self.extents[2:])),
                                      self.tick_inc[1])
                self.m.drawmeridians(meridians, labels=[0, 0, 0, 1],
                                     fontdict=self.axes_font, linewidth=self.lw)  # linewidth = 0 表示无网格
                self.m.drawparallels(parallels, labels=[1, 0, 0, 0],
                                     fontdict=self.axes_font, linewidth=self.lw)
            # 画海岸线和陆地
            self.m.drawcoastlines()
            self.m.drawmapboundary(linewidth=3)
            self.m.fillcontinents(color='tan')
        else:
            self.ax.set_xticks(np.arange(self.extents[0], self.extents[1] + self.tick_inc[0], self.tick_inc[0]))
            self.ax.set_yticks(np.arange(self.extents[2], self.extents[3] + self.tick_inc[1], self.tick_inc[1]))
        # 添加水深
        if self.depth:
            self._add_depth_data()

    def _add_depth_data(self):
        """
        功能：figure中添加水深数据
        :return:
        """
        # 读取水深数据
        depth_file = r'H:\depth_data\ETOPO1.nc'
        depth_data = Dataset(depth_file)
        depth_lon = depth_data.variables['x'][:]
        depth_lat = depth_data.variables['y'][:]
        depth = depth_data.variables['z'][:]
        # 选择指定区域
        lat_index_down = np.where(depth_lat > np.min(self.extents[-2:]))[0][0]
        lat_index_up = np.where(depth_lat < np.max(self.extents[-2:]))[0][-1]
        lon_index_left = np.where(depth_lon > np.min(self.extents[:2]))[0][0]
        lon_index_right = np.where(depth_lon < np.max(self.extents[:2]))[0][-1]
        select_lat = depth_lat[lat_index_down:lat_index_up+1]
        select_lon = depth_lon[lon_index_left:lon_index_right+1]
        select_depth = depth[lat_index_down:lat_index_up+1, lon_index_left:lon_index_right+1]
        depth_data.close()
        # 水深大于0的设为0，然后水深取倒数
        select_depth[np.where(select_depth > 0)] = 0
        select_depth = np.abs(select_depth)
        # 在basemap中作图
        m_lon, m_lat = np.meshgrid(select_lon, select_lat)
        mm_lon, mm_lat = self.m(m_lon, m_lat)
        self.ax.contourf(mm_lon, mm_lat, select_depth, 6, cmap=cm.deep)
        levels = np.array([50, 500, 1500, 5000, 6000])
        contour = self.ax.contour(mm_lon, mm_lat, select_depth, levels, colors='k', linewidths=0.5)
        # 移除等高线中较小的线
        for level in contour.collections:
            for kp, path in reversed(list(enumerate(level.get_paths()))):
                verts = path.vertices
                diameter = np.max(verts.max(axis=0) - verts.min(axis=0))
                if diameter < 1000000:    # 1000000
                    del(level.get_paths()[kp])
        self.ax.clabel(contour, inline=1, fmt='%1.0f', fontsize=15, colors='k')

    def plot_lines(self, x, y, *args, **kwargs):
        """
        功能：画折线图，基于basemap或者笛卡尔坐标系
        :return:
        """
        if not self.cartesian:
            base_x, base_y = self.m(x, y)
        else:
            base_x, base_y = x, y

        self.line_plot = self.ax.plot(base_x, base_y, *args, **kwargs)
        plt.show()

    def plot_sms_grid(self, mesh_2dm, *args, **kwargs):
        """
        功能：画网格图
        参数：
        :param mesh_2dm: 网格路径
        :param args:
        :param kwargs:
        :return:
        """
        domain = Domain(mesh_2dm, native_coordinates='spherical')
        x, y = self.m(domain.grid.lon, domain.grid.lat)
        self.tripcolor_plot = self.ax.tripcolor(x, y, domain.grid.triangles,
                                                  facecolors=-domain.grid.h_center,
                                                      *args, **kwargs)
        cbar = self.ax.coloarbar(self.tripcolor_plot)
        cbar.ax.tick_params(labelsize=15)
        if self.cb_label:
            cbar.set_label(self.cb_label, fontdict=self.ax_font)

