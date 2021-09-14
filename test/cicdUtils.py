# -*- coding: utf-8 -*-
"""
@File    : cicdUtils.py
@Time    : 2021/6/17:16:12
@Author  : liuyuanlong
@Licence : (C) Copyright 2019-2020, ZettaCloud Xi'an
@Desc    : 
"""
import argparse
from ftplib import FTP
import os


class CICDUtils:
    def ftpconnect(self, host, username, password):
        ftp = FTP()  # 设置变量
        timeout = 30
        port = 21
        ftp.connect(host, port, timeout)  # 连接FTP服务器
        ftp.login(username, password)  # 登录
        self.ftp = ftp
        return ftp

    def downloadfile(self, ftp, remotepath, localpath):
        ftp.cwd(remotepath)  # 设置FTP远程目录(路径)
        list = ftp.nlst()  # 获取目录下的文件,获得目录列表
        for name in list:
            print(name)
            path = localpath + name  # 定义文件保存路径
            f = open(path, 'wb')  # 打开要保存文件
            filename = 'RETR ' + name  # 保存FTP文件
            ftp.retrbinary(filename, f.write)  # 保存FTP上的文件
            f.close()


    def get_dir_and_files(self, ftp_path):
        # 获取路径的文件夹和文件
        path_info = []
        folder = []
        files = []
        try:
            self.ftp.dir(ftp_path, path_info.append)
        except Exception as e:
            print('Get ftp dir fail:{}'.format(e))
            print('Fail path:{}'.format(ftp_path))
        for path in path_info:
            path = path.strip()
            filename = ftp_path + '/' + path.split(':')[1][3:]
            if path.startswith('-'):
                files.append(filename)
            elif path.startswith('d'):
                folder.append(filename)
            else:
                print('Can not tell whether it is a folder or a file:{}'.format(path))
        return folder, files

    def create_folder(folder):
        folder = os.path.abspath(folder)
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                print('Create folder success:{}'.format(folder))
            except Exception as e:
                print('Create folder fail:{}'.format(e))

    def down_file(self, ftp_file, save_local_path):
        success = False
        abs_path = os.path.abspath(save_local_path)
        path = os.path.dirname(save_local_path)
        self.create_folder(path)
        try:
            with open(abs_path, 'wb') as f:
                ret = self.ftp.retrbinary('RETR ' + ftp_file, f.write)  # 下载文件
                print('Down ftp file return:{}'.format(ret))
                if ret.startswith('226'):
                    print('Down ftp file success, save to:{}'.format(abs_path))
                    success = True
        except Exception as e:
            print('Down ftp file fail:{}'.format(e))
            print('Fail path:{}'.format(ftp_file))
            success = False
        return success

    def down_folder(self, ftp_path, local_path):
        # 下载文件夹
        local_path = os.path.abspath(local_path)
        dirs, all_file = self.get_dir_and_files(ftp_path)
        for one_dir in dirs:
            self.down_folder(one_dir, local_path)
        for one_file in all_file:
            save_path = local_path + one_file
            self.down_file(one_file, save_path)


    def initParam(self):
        parser = argparse.ArgumentParser(description='List the content of ftp')
        parser.add_argument('--ftp', type=str, default='ftp.zettacloud.com', help='ftp info')
        parser.add_argument('--user', type=str, default='anonymous')
        parser.add_argument('--password', type=str, default='')
        parser.add_argument('--remotePath', type=str, default='windows/nsis/nsis.zip')
        parser.add_argument('--localPath', type=str, default='./')
        args = parser.parse_args()
        return args


if __name__ == '__main__':
    ci = CICDUtils()
    args = ci.initParam()
    print(args)
    ftp = ci.ftpconnect(args.ftp, args.user, args.password)
    ci.downloadfile(ftp,args.remotePath, args.localPath)
