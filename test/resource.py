# -*- coding: utf-8 -*-

import pickle
import platform
import tkinter as tk
import tkinter.messagebox

import win32com
import wmi
import pynvml

window = tk.Tk()

window.title('资源配置修改')

window.geometry('500x450')

tk.Label(window, text='系统总资源概览', font=('Arial', 16)).pack()

tk.Label(window, text='CPU核数(单位:核):', font=('Arial', 14)).place(x=40, y=170)
tk.Label(window, text='内存大小(单位:MB):', font=('Arial', 14)).place(x=40, y=210)
tk.Label(window, text='磁盘大小(单位:MB):', font=('Arial', 14)).place(x=40, y=250)
tk.Label(window, text='显卡型号:', font=('Arial', 14)).place(x=40, y=290)
tk.Label(window, text='显卡个数:', font=('Arial', 14)).place(x=40, y=330)
# 资源展示框
# var_usr_source = tk.StringVar()
# entry_usr_source = tk.Entry(window, textvariable=var_usr_source, font=('Arial', 14))
# entry_usr_source.place(x=100, y=100)

# CPU值输入框
var_usr_cpu = tk.StringVar()
entry_usr_cpu = tk.Entry(window, textvariable=var_usr_cpu, font=('Arial', 14))
entry_usr_cpu.place(x=215, y=175)
# 内存值输入框
var_usr_mem = tk.StringVar()
entry_usr_mem = tk.Entry(window, textvariable=var_usr_mem, font=('Arial', 14))
entry_usr_mem.place(x=215, y=215)
# 硬盘值输入框
var_usr_disk = tk.StringVar()
entry_usr_disk = tk.Entry(window, textvariable=var_usr_disk, font=('Arial', 14))
entry_usr_disk.place(x=215, y=255)
# 显卡值类型输入框
var_usr_nvidia = tk.StringVar()
entry_usr_nvidia = tk.Entry(window, textvariable=var_usr_nvidia, font=('Arial', 14))
entry_usr_nvidia.place(x=215, y=295)
# 显卡个数输入框
var_usr_nvidia_num = tk.StringVar()
entry_usr_nvidia_num = tk.Entry(window, textvariable=var_usr_nvidia_num, font=('Arial', 14))
entry_usr_nvidia_num.place(x=215, y=335)

app_local_app = "F:\idps-core\config\application-local.properties"


class Win32Info(object):

    def __init__(self):
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer(".", "root\cimv2")

    def collect(self):
        data = {
            'os_type': platform.system(),
            'os_release': "%s %s  %s " % (platform.release(), platform.architecture()[0], platform.version()),
            'os_distribution': 'Microsoft',
            'asset_type': 'server'
        }

        data.update(self.get_cpu_info())
        data.update(self.get_ram_info())
        data.update(self.get_disk_info())
        # data.update(self.get_nvidia_info())

        return data

    def get_cpu_info(self):
        data = {}
        cpu_lists = self.wmi_obj.Win32_Processor()
        cpu_core_count = 0
        for cpu in cpu_lists:
            cpu_core_count += cpu.NumberOfCores
        data["CPU CORE"] = cpu_core_count * 2  # CPU总的线程数
        return data

    def get_ram_info(self):
        data = []
        # 这个模块用SQL语言获取数据
        ram_collections = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")
        for ram in ram_collections:  # 主机中存在很多根内存，要循环所有的内存数据
            ram_size = int(int(ram.Capacity) / (1024 ** 2))  # 转换内存单位为MB
            item_data = {
                # "slot": ram.DeviceLocator.strip(),
                "capacity": ram_size,
                "model": ram.Caption,
            }
            data.append(item_data)  # 将每条内存的信息，添加到一个列表里

        return {"MEM": ram_size}  # 再对data列表封装一层，返回一个字典，方便上级方法的调用

    def get_disk_info(self):
        data = []
        for disk in self.wmi_obj.Win32_DiskDrive():  # 每块硬盘都要获取相应信息
            disk_data = {}
            disk_data['capacity'] = int(int(disk.Size) / (1024 ** 3))
            data.append(disk_data)

        return {'DISK': data}

    def write_file(self, file_path, data):
        with open(file_path, "w") as file:
            for info in data:
                file.write(info+":"+str(data[info]) + "\n")
                print(info+":"+str(data[info]))


    def get_nvidia_info(self):
        w = wmi.WMI()
        for video in w.Win32_VideoController():
            print(video)
            print("GPU NAME: %s" % video.caption)  #
            print("GPU RAM: %d" % abs(video.AdapterRAM/1024/1024))


if __name__ == "__main__":
    data = Win32Info().collect()
    for key in data:
        print(key, ":", data[key])
    Win32Info().write_file("test.txt", data)
    Win32Info().get_nvidia_info()


# 定义用户取消按钮操作
def usr_cancel():
    tkinter.messagebox.showinfo('cancel', '取消设置!')


# 定义用户保存信息功能
def usr_save():
    def save_to_rsmatrix():
        # 获取用户输入的各项指标
        var_id = entry_usr_cpu.get()
        # var_id = entry_usr_disk.get()
        # var_id = entry_usr_mem.get()
        app_local = open(app_local_app, 'a+', encoding='utf-8')
        app_local.write(var_id + '\n')
        app_local.close()


def usr_save():
    def usr_source():
        cpu_info = entry_usr_cpu.get()
        mem_info = entry_usr_mem.get()
        disk_info = entry_usr_disk.get()
        nvidia_info = entry_usr_nvidia.get()
        nvidia_num = entry_usr_nvidia_num.get()
        with open('application-local.properties', 'rb') as usr_file:
            app_info = pickle.load(usr_file)

    tkinter.messagebox.showinfo('source', '资源设置成功!')


# cancel and save  按钮
btn_cancel = tk.Button(window, text='取消', command=usr_cancel)
btn_cancel.place(x=100, y=380)
btn_save = tk.Button(window, text='保存并退出', command=usr_save)
btn_save.place(x=360, y=380)

# 进入主循环
window.mainloop()
