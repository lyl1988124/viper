# -*- coding: utf-8 -*-
"""
@File    : upgrade_idps.py
@Time    : 2021/8/16:15:14
@Author  : liuyuanlong
@Licence : (C) Copyright 2019-2020, ZettaCloud Xi'an
@Desc    : 自动化升级工具
"""
import datetime
import os
import re
import shutil
import sys
import time
import zipfile
from subprocess import Popen


class UpgradeIdps(object):
    configDict = {'db_host': '127.0.0.1',
                  'db_port': '15432',
                  'db_name': 'idps',
                  'db_user': 'postgres',
                  'db_pw': 'db_zettacloud',
                  'conda_env': 'C:\ProgramData\Anaconda3\envs',
                  'unzip_pw': 'idps.zettacloud.deploy',
                  'idps_home_path': os.path.abspath('../'),
                  'upgrade_file_path': ''
                  }

    jar_path = 'idps-core/bin/idps-starter.jar'
    portal_path = 'idps-portal/nginx-1.16.1'
    domseg_path = 'idps-executor/domseg'
    domseg_backup = 'idps-executor/operator_backup'

    backup_list = {jar_path, portal_path, domseg_path, domseg_backup}
    upgrade_list = {jar_path, portal_path, domseg_path, domseg_backup}

    def __init__(self):

        upgrade_conf_file = 'upgrade_config'
        if not os.path.isfile(upgrade_conf_file):
            print("系统使用默认配置")
        else:
            try:
                with open(upgrade_conf_file, encoding='utf-8', mode='r') as file:
                    lines = file.readlines()
                    for line in lines:
                        if "#" in line:
                            continue
                        confInfo = line.strip().split("=")
                        if len(confInfo[1]) == 0:
                            continue
                        self.configDict.update({confInfo[0]: confInfo[1]})
                    print(self.configDict)
                    time.sleep(1)
            finally:
                file.close()

    def unzipUpgrade(self, srcPath):

        print("开始解压升级文件...")

        try:
            if not zipfile.is_zipfile(srcPath):
                print("压缩包非法")

            srcAbdPath = os.path.abspath(srcPath)
            index = srcAbdPath.rfind("\\")
            firstDstPath = os.path.abspath(srcAbdPath[0:index])

            print("scrPath=" + srcPath + " dstPath=" + firstDstPath)

            # 获取unzip工具的绝对路径
            unzip_abs_path = os.path.abspath("./tools/7z")
            print(unzip_abs_path)

            firstUnzipCmd = unzip_abs_path + " x -y -p" + self.configDict[
                'unzip_pw'] + " -o" + firstDstPath + " " + srcPath
            #print("firstUnzipCmd=" + firstUnzipCmd)
            p1 = Popen(firstUnzipCmd, shell=True)
            p1.wait()

            dstDir = srcPath[0:srcPath.rfind(".")]

            file_list = []
            for filename in os.listdir(dstDir):
                abs_path = os.path.join(dstDir, filename)
                print(abs_path)
                if ".zip" in abs_path:
                    file_list.append(abs_path)

            secondSrcPath = file_list[0]
            secondIndex = secondSrcPath.rfind("\\")
            secondDstPath = secondSrcPath[0:secondIndex]

            print("secondSrcPath=" + secondSrcPath + " secondDstPath=" + secondDstPath)

            secondUzipCmd = unzip_abs_path + " x -y -p" + self.configDict[
                'unzip_pw'] + " -o" + secondDstPath + " " + secondSrcPath
            #print("secondUnzipCmd=" + secondUzipCmd)
            p2 = Popen(secondUzipCmd, shell=True)
            p2.wait()

            secondIndex = secondSrcPath.rfind("\\")

            unzipPath = secondDstPath + "/" + secondSrcPath[secondIndex + 1:-4]
            print(unzipPath)

        except Exception as e:
            print(e)
            print("升级文件解压失败！")
            os.system("pause")

        print("升级文件解压完成！")

        return unzipPath

    def dbBackup(self):

        print("开始备份数据库...")

        try:
            backup_path = "pgsql_backup"
            today = backup_path + time.strftime('%Y-%m-%d')
            bakFile = today + os.sep + time.strftime('%Y-%m-%d') + '_' + self.configDict['db_name'] + '.backup'

            # 创建备份目录
            if not os.path.exists(today):
                Msg = '-' * 30 + time.strftime('%Y-%m-%d,%H:%M:%S') + '-' * 30 + '\n'
                if (os.mkdir(today)) == None:
                    Msg += '** 成功创建备份目录： ' + today + '\n\n'
                    print(Msg)
                else:
                    Msg += '!! 创建备份目录： ' + today + '失败，请检查目录是否可写！\n\n'
                    print(Msg)
                    sys.exit()
            # 获取pg_dump工具的绝对路径
            pg_tool_path = os.path.abspath(".\\tools\\pgsql\\")
            print(pg_tool_path)

            # 备份idps数据库
            cmd_dump = "%s\\pg_dump -i -h %s -p %s -U %s -F c -b -v -f %s %s" % \
                       (pg_tool_path,
                        self.configDict['db_host'],
                        self.configDict['db_port'],
                        self.configDict['db_user'],
                        bakFile,
                        self.configDict['db_name'])

            print(cmd_dump)

            cmd_dump = "set PGPASSWORD=%s&& %s" % \
                       (self.configDict['db_pw'],
                        cmd_dump)

            # 执行备份命令
            p = Popen(cmd_dump, shell=True)
            p.wait()
            if p.stderr is None:
                print('数据备份为： ' + bakFile + '\n')
            else:
                print('数据备份失败！\n')

        except Exception as e:
            print(e)
            print("数据库更新失败！")
            os.system("pause")

        print("数据库备份完成")

    def executeUpgradeSqlFile(self, unzipPath):

        print("开始更新数据库...")

        try:
            # 获取pg工具的绝对路径
            pg_tool_path = os.path.abspath(".\\tools\\pgsql\\")
            print(pg_tool_path)

            sql_file_path = os.path.join(unzipPath, 'idps/idps-core/sql/idps-upgrade.sql')

            # 执行sql文件
            cmd_upgrade = "%s\\psql -h %s -p %s -U %s -d %s -f %s" % \
                          (pg_tool_path,
                           self.configDict['db_host'],
                           self.configDict['db_port'],
                           self.configDict['db_user'],
                           self.configDict['db_name'],
                           sql_file_path)

            print(cmd_upgrade)

            cmd_upgrade = "set PGPASSWORD=%s&& %s" % \
                          (self.configDict['db_pw'],
                           cmd_upgrade)

            # 执行sql
            p = Popen(cmd_upgrade, shell=True)
            p.wait()
            if p.stderr is None:
                print('sql 执行成功')
            else:
                print('sql 执行失败！\n')

        except Exception as e:
            print(e)
            print("数据库更新失败！")
            os.system("pause")

        print("数据库更新完成...")

    def backupIdps(self):

        print("开始备份idps...")

        try:
            # 设置需要备份文件的路径
            idps_home = self.configDict['idps_home_path']

            date = datetime.date.today()
            for file in self.backup_list:
                origin_file_name = os.path.join(idps_home, file)

                if not os.path.exists(origin_file_name):
                    print("file not exist. filePath=" + origin_file_name)
                    continue

                new_file_name = file + "-backup" + "-" + str(date)
                new_file_name = os.path.join(idps_home, new_file_name)
                os.rename(origin_file_name, new_file_name)

                print("origin_file_name=" + origin_file_name + " new_file_name=" + new_file_name)

        except Exception as e:
            print(e)
            print("idps 备份失败!")
            os.system("pause")

        print("idps 备份完成")

    def copyUpgradeToIdps(self, unzipPath):

        print("开始复制新idps...")

        try:
            idps_home = self.configDict['idps_home_path']
            upgrade_path = os.path.join(unzipPath, 'idps')

            for file in self.upgrade_list:
                idps_file_name = os.path.join(idps_home, file)
                upgrade_file_name = os.path.join(upgrade_path, file)
                self.copyFile(upgrade_file_name, idps_file_name)

        except Exception as e:
            print(e)
            print("idps 更新失败!")
            os.system("pause")

        print("idps 更新完成")

    def copyFile(self, src_path, dst_path):

        if not os.path.isfile(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)
        print("copy %s -> %s" % (src_path, dst_path))

    def updateCondaEnv(self, unzipPath):

        print("开始更新 conda env")

        try:
            # 获取unzip工具的绝对路径
            unzip_abs_path = os.path.abspath("./tools/7z")
            print(unzip_abs_path)

            dstDir = self.configDict['conda_env']
            repository_path = os.path.join(unzipPath, 'idps/idps-executor/package/repository')

            files = os.listdir(repository_path)
            print(files)

            envList = []
            for file in files:
                if ".zip" not in file and not zipfile.is_zipfile(file):
                    print("not zip file = " + file)
                    continue
                zipFile = os.path.join(repository_path, file)
                print(zipFile)

                unzipCmd = unzip_abs_path + " x -y -p" + self.configDict[
                    'unzip_pw'] + " -o" + dstDir + " " + zipFile
                print(unzipCmd)
                p = Popen(unzipCmd, shell=True)
                p.wait()

                envName = dstDir + "/" + file[0:-4]
                envList.append(envName)

            conda_env = ";".join(envList)
            print(conda_env)

            # 设置环境变量，需要以管理员身份运行
            command = r"setx IDPS_CONDA_ENV_ROOT %s /m" % conda_env
            os.system(command)

        except Exception as e:
            print(e)
            print("conda env 更新失败!")
            os.system("pause")

        print("conda env 更新成功！")

    def backupAndUpdateCondaEnv(self):
        idps_conda_env = os.environ.get('IDPS_CONDA_ENV_ROOT')
        command = r"setx IDPS_CONDA_ENV_ROOT_BAK %s /m" % idps_conda_env
        os.system(command)

    def checkUpgradeInCorrectDirectory(self):

        # 根据上级目录判定升级包是否在正确目录
        print(os.listdir('../'))
        idps_core_path = os.path.exists('../idps-core')
        idps_portal_path = os.path.exists('../idps-portal')
        idps_executor_path = os.path.exists('../idps-executor')
        if not (idps_core_path and idps_portal_path and idps_executor_path):
            print("请将升级包放在正确目录！")
            os.system("pause")
            raise Exception("请将升级包放在正确目录！")

        upgrade_path = '';
        for filename in os.listdir("."):
            if re.match('.*deploy.*.zip', filename):
                print(filename)
                upgrade_path = filename

        if len(upgrade_path) == 0:
            upgrade_path = upgrade.configDict['upgrade_file_path']

        if len(upgrade_path) == 0:
            print("未检测到升级文件！")
            os.system("pause")
            raise Exception("未检测到升级文件！")

        return upgrade_path


if __name__ == '__main__':
    upgrade = UpgradeIdps()

    # 检查升级包是否在正确目录
    path = upgrade.checkUpgradeInCorrectDirectory()

    # 解压
    unzipPath = upgrade.unzipUpgrade(path)
    #
    # 备份数据库
    upgrade.dbBackup()
    #
    # 备份idps
    upgrade.backupIdps()

    # 备份环境变量 2.5.1环境变量未变化
    # upgrade.backupAndUpdateCondaEnv()

    # 执行sql
    upgrade.executeUpgradeSqlFile(unzipPath)

    # 更新idps
    upgrade.copyUpgradeToIdps(unzipPath)

    # 更新conda env
    # upgrade.updateCondaEnv(unzipPath)
    #
    print("升级程序执行完成！")
    os.system('pause')
