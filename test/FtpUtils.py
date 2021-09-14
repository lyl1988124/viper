# -*- coding: utf-8 -*-
"""
@File    : FtpUtils.py
@Time    : 2021/6/17:17:36
@Author  : liuyuanlong
@Licence : (C) Copyright 2019-2020, ZettaCloud Xi'an
@Desc    : 
"""
import argparse
import ftplib
import os

ROOT = 'ROOT'


class FTPOperate:

    def init(self, ip, port, user, password):
        self.ip = ip
        self.port = int(port)
        self.user = user
        self.password = password
        self.ftp = ftplib.FTP()  # new一个ftp对象

    def connect(self):
        try:
            self.ftp.connect(self.ip, self.port)  # 连接ftp
            print('Connection ftp success')
        except Exception as e:
            print('Connection ftp fail:{}'.format(e))

    def login(self):
        try:
            self.ftp.login(self.user, self.password)  # 登录ftp
            print('Login ftp success')
        except Exception as e:
            print('Login ftp fail:{}'.format(e))

    def cwd_root(self):
        try:
            self.ftp.cwd('/')  # 切换到根目录
            print('Cd ftp root success')
        except Exception as e:
            print('Cd ftp root fail:{}'.format(e))

    def cwd(self, path, relative=''):
        """
        Switch relative to the root directory if relative is ROOT,
        or switch relative to the current directory
        :param path:
        :param relative:
        :return:
        """
        if relative.upper() == ROOT:
            self.cwd_root()
        try:
            self.ftp.cwd(path)  # 切换到任意目录
            print('Cd ftp dir success:{}'.format(path))
        except Exception as e:
            print('Cd ftp dir fail:{}'.format(e))

    def pwd(self):
        current_dir = ''
        try:
            current_dir = self.ftp.pwd()  # 获取当前的目录
            print('Get ftp current dir success:{}'.format(current_dir))
        except Exception as e:
            print('Get ftp current dir fail:{}'.format(e))
        return current_dir

    def close(self):
        try:
            self.ftp.close()  # 关闭
            print('Close ftp success')
        except Exception as e:
            print('Close ftp fail:{}'.format(e))

    @staticmethod
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
        parser.add_argument('--port', type=int, default='21')
        parser.add_argument('--remotePath', type=str, default='windows/nsis/nsis.zip')
        parser.add_argument('--localPath', type=str, default='./aaa')
        args = parser.parse_args()
        return args


def debug():
    ip = '172.16.30.18'
    port = '21'
    user = 'anonymous'
    password = ''
    ftp = FTPOperate(ip, port, user, password)
    ftp.connect()
    ftp.login()
    ftp.pwd()
    ftp.down_file('windows/nsis/nsis.zip', './')
    ftp.down_folder('windows/chrome', './')
    ftp.close()


if __name__ == '__main__':
    ftp = FTPOperate()
    args = ftp.initParam()
    print(args)
    ftp.init(args.ftp, args.port, args.user, args.password)
    ftp.connect()
    ftp.login()
    ftp.pwd()
    ftp.down_file(args.remotePath, args.localPath)
    ftp.close()
