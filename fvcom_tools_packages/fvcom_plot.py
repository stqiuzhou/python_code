#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = model_plot.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/3 22:04

import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator
from netCDF4 import Dataset
from cmocean import cm
import logging
from fvcom_tools_packages.fvcom_grid import Grid
import seaborn as sns

logger = logging.getLogger(__name__)


class PlotFigure(object):
    """
    功能：画各种类型的图
    方法：
    1. plot_lines —— 画折线图
    """
    def __init__(self, grid_path=None, figure=None, axes=None, figsize=(12, 8),
                 extents=None, title=None, title_font=None, ax_font=None,
                 m=None, cartesian=False, tick_inc=None, grid=False,
                 depth=False, cb_label=None, x_label=None, y_label=None,
                 legend_label=None):
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
        :param x_label: x坐标轴的标签
        :param y_label: y坐标轴的标签
        :param legend_label: legend 标签, 输入格式：tuple或者array
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
        self.grid_path = grid_path
        self.x_label = x_label
        self.y_label = y_label
        self.legend_label = legend_label

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
        # 读取网格
        if self.grid_path:
            self.grid = Grid(self.grid_path)

    def _init_figure(self):
        # 初始化图像
        if self.fig is None:
            self.fig = plt.figure(figsize=self.figsize)
        if self.ax is None:
            # 四个参数为坐下宽高相对整体figure的大小
            self.ax = self.fig.add_subplot(111)
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
            if self.grid:
                self.ax.grid()


        # 添加水深
        if self.depth:
            self._add_depth_data()

        # 添加xy坐标轴的标签
        if self.x_label is not None:
            self.ax.set_xlabel(self.x_label)
        if self.y_label is not None:
            self.ax.set_ylabel(self.y_label)

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

    def plot_lines(self, x, y, time_series=False, double_yaxis=False, double_y=None,
                   double_ylabel=None, *args, **kwargs):
        """
        功能：画折线图，基于basemap或者笛卡尔坐标系
        :param x: 横坐标的值
        :param y：纵坐标的值
        :param time_series： 判断x轴是不是时间类型
        :param double_yaxis: 判断是否需要双y轴
        :param legends: legends 标签
        :return:
        """
        if not self.cartesian:
            base_x, base_y = self.m(x, y)
        else:
            base_x, base_y = x, y
        line_plot, = self.ax.plot(base_x, base_y, *args, **kwargs)

        if time_series:
            self.ax.set_xlabel('Times', fontdict=self.axes_font)
            self.set_time_xaxis()

        if double_yaxis:
            ax2 = self.ax.twinx()
            line_plot2, = ax2.plot(x, double_y, 'r')
            ax2.set_ylabel(double_ylabel)
            self.ax.legend((line_plot, line_plot2), self.legend_label, loc='upper center')

    def plot_sms_grid(self, mesh_2dm, *args, **kwargs):
        """
        功能：画网格图
        参数：
        :param mesh_2dm: 网格路径
        :param args:
        :param kwargs:
        :return:
        """
        x, y = self.m(self.grid.lon, self.grid.lat)
        self.tripcolor_plot = self.ax.tripcolor(x, y, self.grid.tri,
                                                  facecolors=-self.grid.h_center,
                                                      *args, **kwargs)
        cbar = self.ax.colorbar(self.tripcolor_plot)
        cbar.ax.tick_params(labelsize=15)
        if self.cb_label:
            cbar.set_label(self.cb_label, fontdict=self.axes_font)

    def plot_surface(self, x, y, values, *args, **kwargs):
        """
        功能：画空间分布的图，例如pcolor，contour等
        :param x: 一般指经度
        :param y: 一般指纬度
        :param values: 参数值
        :param args:
        :param kwargs:
        :return:
        """
        xx, yy = self.m(x, y)
        if self.grid:
            surface_plot = self.ax.tripcolor(xx, yy, self.grid.tri,
                                      facecolors=values, cmap=plt.cm.jet,
                                      *args, **kwargs)
        else:
            surface_plot = self.ax.pcolor(xx, yy, values, cmap=plt.cm.jet,
                                          *args, **kwargs)
        self.set_colorbar(surface_plot)

    def plot_quiver(self, u, v, grid=False, *args, **kwargs):
        x, y = self.m(self.grid.lonc, self.grid.latc)

    def plot_windDir_time(self, time, spd, dir, interval=1, *args, **kwargs):
        """
        功能：画风速风向的时间序列图
        :param time: 时间
        :param spd: 风速
        :param dir: 风向
        :param args:
        :param kwargs:
        :return:
        """
        u = spd * np.sin(np.deg2rad(dir))
        v = spd * np.cos(np.deg2rad(dir))
        Q = self.ax.quiver(time, 2, u, v, width=0.003, scale=80, *args, **kwargs)
        self.ax.quiverkey(Q, 0.1, 0.7, 5, '5 m/s', fontproperties=self.axes_font)
        self.ax.set_xlabel('Times', fontdict=self.axes_font)
        self.ax.yaxis.set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.set_time_xaxis(time_interval=interval)

    def set_time_xaxis(self, time_interval=1):
        """
        功能：添加时间作为x轴的tick
        :param time_interval: 日期显示的间隔
        :return:
        """
        self.ax.xaxis.set_major_locator(DayLocator(interval=time_interval))
        self.ax.xaxis.set_major_formatter(DateFormatter('%m/%d/%H'))
        self.fig.autofmt_xdate()


    def set_colorbar(self, plot_object):
        """
        功能：添加colorbar
        :param plot_object: 需要添加colorbar的对象
        :return:
        """
        cbar = self.fig.colorbar(plot_object)
        plot_object.set_clim(vmin=0, vmax=18)
        if self.cb_label:
            cbar.set_label(self.cb_label, fontdict=self.axes_font)

    def subolots_adjust(self, left=0.18, wspace=0.25, hspace=0.25,
                    bottom=0.13, top=0.91, *args, **kwargs):
        """
        功能：调整子图周围的距离
        :param left: 左边界
        :param wspace: 子图之间的横向间距
        :param hspace: 自如之间的纵向间距
        :param bottom: 下边界
        :param top: 上边界
        :param args:
        :param kwargs:
        :return:
        """
        plt.subplots_adjust(left=left, wspace=wspace, hspace=hspace,
                            bottom=bottom, top=top, *args, **kwargs)

    def show(self):
        """
        功能：显示图片
        :return:
        """
        plt.tight_layout()
        plt.show()

    def save(self, name, *args, **kwargs):
        """
        功能：存储图片
        :param name: 图片路径名
        :param args:
        :param kwargs:
        :return:
        """
        self.fig.savefig(name, bbox_inches='tight', transparent=True, *args, **kwargs)

