#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# __NAME__   = download_ecmwf_ERA-5.py
# __AUTHOR__ = 'QIU ZHOU'
# __TIME__   = 2019/6/29 13:52 

import cdsapi
import os
import datetime
import urllib3

urllib3.disable_warnings()

c = cdsapi.Client()

# 起始日期
begin = datetime.date(1993, 1, 1)
end = datetime.date(1993, 12, 31)
d = begin
delta = datetime.timedelta(days=31)

# 建立下载日期序列
links = []
while d <= end:
    riqi = d.strftime("%Y%m")
    links.append(str(riqi))
    d += delta

for ilink in links:
    main_path = os.path.join(r'E:\ecmwf_ERA5\wind', ilink[:4])
    if not os.path.exists(main_path):
        os.makedirs(main_path)
    target_filename = os.path.join(main_path, 'era5.wind.'+ ilink + '.nc')
    if not os.path.isfile(target_filename):
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'variable':['10m_u_component_of_wind',
                            '10m_v_component_of_wind'],
                'product_type':'reanalysis',
                'year': ilink[:4],
                'month': ilink[-2:],
                'day':[
                    '01','02','03',
                    '04','05','06',
                    '07','08','09',
                    '10','11','12',
                    '13','14','15',
                    '16','17','18',
                    '19','20','21',
                    '22','23','24',
                    '25','26','27',
                    '28','29','30',
                    '31'
                ],
                    'time':[
                    '00:00','01:00','02:00',
                    '03:00','04:00','05:00',
                    '06:00','07:00','08:00',
                    '09:00','10:00','11:00',
                    '12:00','13:00','14:00',
                    '15:00','16:00','17:00',
                    '18:00','19:00','20:00',
                    '21:00','22:00','23:00'
                ],
                'format':'netcdf'
            },
            target_filename)
