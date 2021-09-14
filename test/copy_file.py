# -*- coding: utf-8 -*-
"""
@File    : copy_file.py
@Time    : 2021/2/8:17:22
@Author  : liuyuanlong
@Licence : (C) Copyright 2019-2020, ZettaCloud Xi'an
@Desc    : 
"""
import os
import shutil
import wmi

source = 'E:\\tools\\ftp\\test\\data_view_test\\case_66_org\\xml-labels-pascal'
target = 'E:\\tools\\ftp\\test\\data_view_test\\case_66\\xml-labels-pascal'
#target = 'F:\\test\\case_66\\images_tif'
if not os.path.exists(target):
    os.makedirs(target)


def _copy_file_(source, target):
    list = os.listdir(source)
    cnt = 0
    for i in range(0, len(list)):
        file_name = list[i]
        # path = os.path.join(source, file_path)
        file_name_array = file_name.split('.')

        file_prefix = file_name_array[0]+'.'+file_name_array[1]
        file_ext = file_name_array[len(file_name_array)-1]

        for j in range(0, 10, 1):
            new_file_name = f"{file_prefix}_{j}.{file_ext}"
            shutil.copy(os.path.join(source, file_name), os.path.join(target, new_file_name))
            print(new_file_name)
            cnt = cnt + 1

    print("cnt=" + str(cnt))

_copy_file_(source, target)
