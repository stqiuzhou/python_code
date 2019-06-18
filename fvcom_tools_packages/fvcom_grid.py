#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = fvcom_grid.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/5 22:36

import numpy as np

class Grid(object):
    def __init__(self, grid_path, native_coordinate='spherical'):
        self.grid_path = grid_path
        self.grid_name = grid_path.split('\\')[-1]
        triangle, nodes, x, y, z, types, nodestrings = self.read_sms_grid()
        self.node = len(nodes)
        self.nele = len(triangle)
        self.obc = len(nodestrings)
        self.x = x
        self.y = y
        self.lon = x
        self.lat = y
        self.h = z
        self.tri = triangle
        self.nv = triangle + 1
        self.nodes = nodes
        self.types = types
        self.open_boundary_nodes = nodestrings
        self.lonc = self.nodes2elems(self.lon, self.tri)
        self.latc = self.nodes2elems(self.lat, self.tri)
        self.xc = self.nodes2elems(self.x, self.tri)
        self.yc = self.nodes2elems(self.y, self.tri)
        self.h_center = self.nodes2elems(self.h, self.tri)
        self.nativeCoords = native_coordinate

    def read_sms_grid(self, nodestrings=True):
        """
        功能：读取sms网格数据
        参数：
        :param nodestrings: 设置Ture表示读取nodestring
        返回：
        :return triangle：每个网格三角形的三个node点，shape（nele，3）
        :return nodes：每个点的编号
        :return X, Y, Z: 每个点的经纬度和水深
        :return types：每一个点的类型，用数字表示，一般情况不用
        :return nodestring: 边界点的node
        """
        sms_data = open(self.grid_path, 'r')
        lines = sms_data.readlines()
        sms_data.close()
        triangles = []
        nodes = []
        types = []
        node_strings = []
        nstring = []
        x = []
        y = []
        z = []
        type_count = 2
        for line in lines:
            line.strip()    # strip()表示去掉字符串头尾空格
            if line.startswith('E3T'):
                ttt = line.split()
                t1 = int(ttt[2]) - 1
                t2 = int(ttt[3]) - 1
                t3 = int(ttt[4]) - 1
                triangles.append([t1, t2, t3])
            elif line.startswith('ND'):
                xy = line.split()
                x.append(float(xy[2]))
                y.append(float(xy[3]))
                z.append(float(xy[4]))
                nodes.append(int(xy[1]))
                types.append(0)
            elif line.startswith('NS'):
                all_types = line.split(' ')
                for node_id in all_types[2:]:
                    types[np.abs(int(node_id) - 1)] = type_count
                    if int(node_id) > 0:
                        nstring.append(int(node_id) - 1)
                    else:
                        nstring.append(np.abs(int(node_id)) - 1)
                        node_strings.append(nstring)
                        nstring = []
                    if int(node_id) < 0:
                        type_count += 1
        # 转化为numpy数组, np.asarray 和 np.array 区别是 前者是cut，或者是copy
        triangle = np.asarray(triangles)
        nodes = np.asarray(nodes)
        types = np.asarray(types)
        node_strings = np.asarray(node_strings).flatten()
        X = np.asarray(x)
        Y = np.asarray(y)
        Z = np.asarray(z)
        if nodestrings:
            return triangle, nodes, X, Y, Z, types, node_strings
        else:
            return triangle, nodes, X, Y, Z, types

    def nodes2elems(self, nodes, tri):
        """
        功能：计算网格中心的经纬度
        参数：
        :param nodes: 计算网格中心所需要的数组
        :param tri: 每个三角网格的3个nodes，shape为（nele，3）
        返回：
        :return elems: 网格中心的经纬度
        """
        if np.ndim(nodes) == 1:
            elems = nodes[tri].mean(axis=1)
        else:
            elems = nodes[..., tri].mean(axis=1)

        return elems

    def write_grid_fvcom(self, output):
        """
        功能：讲mesh的数据写入到FVCOM输入文件中：_cor.dat, _grd.dat, _dep.dat, _obc.data
        参数：
        :param output: 输出路径
        返回：
        :return: 4个文件
        """
        # 获取名字（去除.2dm）
        casename = self.grid_name[:-4]
        # FVCOM 4个输入文件的路径
        cor_file = output + '\\' + casename + '_cor.dat'
        dep_file = output + '\\' + casename + '_dep.dat'
        grd_file = output + '\\' + casename + '_grd.dat'
        obc_file = output + '\\' + casename + '_obc.dat'

        # 文件的header
        header1 = 'Node Number = ' + str(self.node) + '\n'
        header2 = 'Cell Number = ' + str(self.nele) + '\n'
        obc_header = 'OBC Node Number = ' + str(self.obc) + '\n'

        # 处理水深数据
        negative_total = sum(self.h < 0)
        positive_total = sum(self.h > 0)
        if negative_total > positive_total:
            self.h = -self.h
            # print('Flipping depths to be positive down since we have been supplied with mostly negative depths.')

        # 写cor文件
        with open(cor_file, 'w') as f:
            f.write(header1)
            for line in zip(self.lon, self.lat, self.lat):
                f.write('{:.6f} {:.6f} {:.6f}\n'.format(*line))
        # 写depth文件
        with open(dep_file, 'w') as f:
            f.write(header1)
            for line in zip(self.lon, self.lat, self.h):
                f.write('{:.6f} {:.6f} {:.6f}\n'.format(*line))
        # 写grd文件
        with open(grd_file, 'w') as f:
            f.write(header1)
            f.write(header2)
            for i, triangle in enumerate(self.tri, 1):
                f.write('{node:d} {:d} {:d} {:d} {node:d}\n'.format(node=i, *triangle + 1))
            for line in zip(self.nodes, self.lon, self.lat, self.h):
                f.write('{:d} {:.6f} {:.6f}\n'.format(*line))
        # 写obc文件
        with open(obc_file, 'w') as f:
            f.write(obc_header)
            for count, node in zip(np.arange(self.obc)+1, self.open_boundary_nodes):
                f.write('{} {:d} {:d}\n'.format(count, node + 1, 1))
