# -*- coding: utf-8 -*-
import os
import platform
import tkinter as tk
import tkinter.messagebox
import win32com
import wmi
import json
import psutil


class GpuInfo:
    gpuId = 0
    type = ""
    code = ""

    def __init__(self, gpuId, type, code):
        # 定义了两个实例变量
        self.gpuId = gpuId
        self.type = type
        self.code = code


def toJson(gpus):
    result=[]
    for key in gpus:
        tmp = gpus[key].split("_")
        result.append(GpuInfo(tmp[0], "GPU", tmp[1]).__dict__)
    return json.dumps(result, separators=(',', ':'))

def update_properties_file(path, data,gpu):
    org_file = open(path, "r", encoding="utf-8")
    new_path = path + "_bak"
    target_file = open(new_path, "w", encoding='utf-8')
    for content in org_file:
        # print(content)
        if "cpu" in content.lower():
            content = content[0:content.index("=") + 1] + data['cpu'] + "\n"
        if "mem" in content.lower():
            content = content[0:content.index("=") + 1] + data['mem'] + "\n"
        if "disk" in content.lower():
            content = content[0:content.index("=") + 1] + data['disk'] + "\n"
        if "gpu" in content.lower():
            content = content[0:content.index("=") + 1] + toJson(gpu) + "\n"

        target_file.write(content)
    org_file.close()
    target_file.close()

    # 如果文件存在，则删除
    if os.path.exists(path):
        os.remove(path)
    os.rename(new_path, path)


class Win32Info(object):

    def __init__(self):
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer(".", "root\cimv2")

    def collect(self):
        data = {
            'os_type': platform.system(),
            'os_release': "%s %s  %s " % (platform.release(), platform.architecture()[0], platform.version()),
        }
        data.update(self.get_cpu_info())
        data.update(self.get_ram_info())
        data.update(self.get_disk_info())
        return data

    # 获取处理器信息
    def get_cpu_info(self):
        data = {}
        cpu_lists = self.wmi_obj.Win32_Processor()
        cpu_core_count = 0
        for cpu in cpu_lists:
            cpu_core_count += cpu.NumberOfCores
        data["CPU_NUM"] = cpu_core_count * 2  # CPU总的线程数
        return data

    # 获取硬盘信息
    def get_disk_info(self):
        tmplist = []
        c = wmi.WMI()
        for physical_disk in c.Win32_DiskDrive():
            for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                    tmpdict = {}
                    tmpdict["Caption"] = logical_disk.Caption
                    tmpdict["DiskTotal"] = int(logical_disk.Size) / 1024 / 1024 // 1024
                    tmpdict["UseSpace"] = (int(logical_disk.Size) - int(logical_disk.FreeSpace)) / 1024 / 1024 / 1024
                    tmpdict["FreeSpace"] = int(logical_disk.FreeSpace) / 1024 / 1024 / 1024
                    tmpdict["Percent"] = int(
                        100.0 * (int(logical_disk.Size) - int(logical_disk.FreeSpace)) / int(logical_disk.Size))
                    tmplist.append(tmpdict)
        for d in tmplist:
            print(d)
        return tmpdict

    # 获取内存信息
    def get_ram_info(self):

        data = []

        phymem = psutil.virtual_memory()
        line =(str(int(phymem.total / 1024 / 1024)))
        return {"ram": line}

# 获取显卡信息
def get_nvidia_info():
    data = {}
    r = os.popen("nvidia-smi -L")
    nvidia_num=r.read().split("\n")
    print(nvidia_num)
    gpu_data = dict()

    for gpu in nvidia_num:
        if gpu=='':
            continue
        idx = gpu[4: gpu.index(":")]
        name = idx+"_"+gpu.split(":")[1].split("(UUID")[0].strip()
        gpu_data[idx]=name

    return gpu_data


def view_info(data):

    def add():
        # 获取文本框输入内容
        data = {}
        data["cpu"] = entry_usr_cpu.get()
        data["mem"] = entry_usr_mem.get()
        data["disk"] = entry_usr_disk.get()
        org_file = "..\\..\\idps\\idps-core\\config\\application-local.properties"
        update_properties_file(org_file, data,gpu)
        tkinter.messagebox.showinfo('save', '资源设置成功!')

    # 点击勾选框触发
    gpu = {}
    def getselect(item, text):
        if selects[item].get() == True:
            gpu[item] = text
        else:
            gpu.pop(item)
        #print(gpu)

    root = tk.Tk()
    frame1 = tk.Frame(root, pady=130, padx=210)
    frame1.grid(row=10, column=0)
    # 全选反选
    opt = tk.IntVar()
    list1 = get_nvidia_info()
    v = []
    selects = {}
    # 设置勾选框，每四个换行
    for index, item in enumerate(list1):
        #v.append(tk.StringVar())
        selects[item]=tk.BooleanVar()
        entry_usr_gpu=tk.Checkbutton(frame1, text=list1[item], variable=selects[item], command=lambda item=item: getselect(item,list1[item])).grid(row=index // 2 + 1, column=index % 2,sticky='w')
    # CPU值输入框
    entry_usr_cpu = tk.Entry(root, font=('Arial', 12))
    entry_usr_cpu.place(x=260, y=165)
    # 内存值输入框
    entry_usr_mem = tk.Entry(root, font=('Arial', 12))
    entry_usr_mem.place(x=260, y=205)
    # 硬盘值输入框
    entry_usr_disk = tk.Entry(root, font=('Arial', 12))
    entry_usr_disk.place(x=260, y=245)
    root.title('RS_change')
    root.geometry('600x450')
    tk.Label(root, text='当前系统资源参考,另磁盘大小为当前安装路径的磁盘值', font=('Arial', 16),bg='red').grid(row=20)
    tk.Label(root, text='CPU 核数: ' + data['CPU_NUM'] + "C", font=('Arial', 10)).grid(row=11)
    tk.Label(root, text='内存大小(单位:MB): ' + data['ram'] + "MB", font=('Arial', 10)).grid(row=12)
    tk.Label(root, text='硬盘大小(单位:G): ' + data['DiskTotal'] + "G", font=('Arial', 10)).grid(row=13)
    tk.Label(root, text='请勾选要使用的显卡:', font=('Arial', 14)).place(x=30, y=120)
    tk.Label(root, text='请设置CPU核数(单位:核):', font=('Arial', 14)).place(x=30, y=160)
    tk.Label(root, text='请设置内存大小(单位:MB):', font=('Arial', 14)).place(x=30, y=200)
    tk.Label(root, text='请设置磁盘大小(单位:MB):', font=('Arial', 14)).place(x=30, y=240)
    btn_save = tk.Button(root, text="保存", command=add)
    btn_save.place(x=450, y=400)
    root.mainloop()


if __name__ == "__main__":
    data = {}
    data1 = Win32Info().collect()
    for tmp in data1:
        data[str(tmp)] = str(data1[tmp])
    view_info(data)
