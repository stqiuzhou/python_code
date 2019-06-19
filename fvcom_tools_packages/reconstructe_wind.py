#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = reconstructed_wind.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/18 14:30

import numpy as np
from .utily import distance_on_sphere


class Reconstructe(object):

    def __init__(self, lon, lat, lonc, latc, Pc, P1, Vmax,
                 lonc_af, latc_af, dt, theta, Rmax=None, Rk=40,
                 Rmax_mold=1, press_mold=1, move_mold=1):
        """
        功能：重构气压场和风场
        :param lon: 所求点的经度，可接受array
        :param lat: 所求点的纬度，可接受array
        :param lonc: 台风中心的经度
        :param latc: 台风中心的纬度
        :param Pc: 台风中心的气压 hpa
        :param P1: 距离台风中心无限远处的气压，一般设为1010hpa
        :param Vmax: 台风最大风速
        :param lonc_af: 下一个台风中心经度
        :param latc_af: 下一个台风中心纬度
        :param dt:    下一个台风中心与当前台风中心的时间差，一般为6小时
        :param theta: 台风入流角
        :param Rmax:  台风最大风速半径，如果没有给出（None），那就通过方法calculate_Rmax()计算
        :param Rk:    计算台风最大风速半径的经验系数，一般取30-60，仅用于Rmax_mold=1的时候
        :param Rmax_mold: 计算最大风速半径的不同方法, 具体值请参考方法calculate_Rmax()注释
        :param press_mold: 计算气压场的不同方法, 具体值请参考方法air_pressure_field()注释
        :param move_mold: 计算移动风场的不同方法, 具体值请参考方法move_windfield()注释
        """
        self.lon = lon
        self.lat = lat
        self.lonc = lonc
        self.latc = latc
        self.Pc = Pc
        self.P1 = P1
        self.Vmax = Vmax
        self.lonc_af = lonc_af
        self.latc_af = latc_af
        self.dt = dt
        self.theta = theta
        self.Rmax = Rmax
        self.Rk = Rk
        self.Rmax_mold = Rmax_mold
        self.press_mold = press_mold
        self.move_mold = move_mold
        # 常数设置
        self.rol = 1.29           # 空气密度：kg/m3
        self.r_earth = 6371004    # 地球半径 m
        self.omega = 7.292115e-5  # 地球自转角速度 rad/s
        self.f = 2 * self.omega * np.deg2rad(self.lat) # 科氏参数
        self.r = distance_on_sphere(self.lon, self.lat, self.lonc, self.latc)   # 所求点到台风中心的距离

        if self.Rmax is None and self.Rmax_mold:
            self._calculate_Rmax()
        if self.press_mold:
            self._air_pressure_field()
        if self.move_mold:
            self._move_windfild()
            self._gradient_windfild()

    def _calculate_Rmax(self):
        """
        功能：计算最大风速半径
        Rmax_mold = 1 : 高钦钦（2012） 硕士论文
        Rmax_mold = 2 : Graham and Nunn (1959)
        :return:
        """
        if self.Rmax_mold == 1:
            Rmax = self.Rk - 0.4 * (self.Pc - 900) + 0.01 * (self.Pc - 900) ** 2

        if self.Rmax_mold == 2:
            Rmax = 28.25 * np.tanh(0.0873 * (self.lat - 28)) + 12.22 * np.exp((self.Pc - self.P1) / 33.86) \
            + 0.2 * self.Vmax + 37.22

        self.Rmax = 1000 * Rmax  # 单位：m


    def _air_pressure_field(self):
        """
        功能：构建理论气压场
        press_mold = 1 : Fujita (1956)
        press_mold = 2 :
        :return:
        """
        if self.press_mold == 1:
            self.Pr = self.P1 - (self.P1 - self.Pc) / np.sqrt(1 + (self.r / self.Rmax) ** 2)
            # dp/dr
            self.dpdr = (self.P1 - self.Pc) * self.r / self.Rmax ** 2 / (1 + (self.r / self.Rmax) ** 2) ** 1.5

    def _gradient_windfild(self):
        """
        功能：根据气压场计算梯度风
        :return:
        """
        # 梯度风公式
        self.Vg = -self.f * self.r / 2 + np.sqrt(self.f ** 2 / 4 * self.r ** 2 + self.r / self.rol * self.dpdr)
        # 每个点到台风中心点的经纬度方向的距离，单位：m
        dx = self.r_earth * np.deg2rad(self.lon-self.lonc) * np.cos((self.lat + self.latc) * 0.5)
        dy = self.r_earth * np.deg2rad(self.lat - self.latc)
        # u，v方向上的梯度风
        self.u_vg = self.Vg * (dx * np.sin(self.theta) + dy * np.cos(self.theta))
        self.v_vg = self.Vg * (dx * np.cos(self.theta) - dy * np.sin(self.theta))

    def _move_windfild(self):
        """
        功能：计算台风移动风场
        move_mold = 1: ueno (1981)
        :return:
        """
        # 台风最佳路径相邻点之间经纬度方向的距离，单位：m
        dis_x = self.r_earth * np.deg2rad(self.lonc_af - self.lonc) * np.cos(self.latc)
        dis_y = self.r_earth * np.deg2rad(self.latc_af - self.latc)

        if self.move_mold == 1:
            # 经纬度方向的移动风速，单位：m/s
            self.u_mov = dis_x / (3600. * self.dt) * np.exp(-np.pi / 4 * np.abs(self.r - self.Rmax) / self.Rmax)
            self.v_mov = dis_y / (3600. * self.dt) * np.exp(-np.pi / 4 * np.abs(self.r - self.Rmax) / self.Rmax)



    def synthesis_windfield(self, c1=0.8, c2=0.8):
        """
        功能：合成台风模式的风场
        :param c1: 经验参数
        :param c2: 经验参数
        :return:
        """
        wind_x = c1 * self.u_mov - c2 * self.u_vg
        wind_y = c1 * self.v_mov + c2 * self.v_vg
        wind = np.sqrt(wind_x ** 2 + wind_y ** 2)
        return wind

