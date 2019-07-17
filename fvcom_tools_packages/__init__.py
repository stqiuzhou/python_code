#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = __init__.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/17 21:06

import matplotlib.pyplot as plt
import seaborn as sns

# 初始化整体图像
sns.set_style('ticks')
plt.rcParams['font.sans-serif'] = 'Times New Roman'
plt.rcParams['font.size'] = 20
plt.rcParams['figure.dpi'] = 600
plt.rcParams['savefig.dpi'] = 600
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none'
# 初始化标题
plt.rcParams['axes.titlesize'] = 25
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlepad'] = 15
# 初始化坐标轴
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['ytick.labelsize'] = 15
# 初始化legend
plt.rcParams['legend.fontsize'] = 20
plt.rcParams['legend.title_fontsize'] = 20
# 初始化线条
plt.rcParams['lines.linewidth'] = 1.5


