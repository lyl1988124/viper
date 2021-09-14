from tkinter import *
import json
import os

def checkBox():
    root = Tk()
    Label(root, text='请选择你喜欢的食物').grid(row=1)

    # 创建食物的字典
    food = {0: '蛋炒饭', 1: '红烧肉', 2: '油波面', 3: '羊肉串', 4: '大盘鸡'}
    selects = {}
    for i in range(len(food)):
        selects[i] = BooleanVar()
        Checkbutton(root, text=food[i], variable=selects[i]).grid(row=i + 2)

    for key, value in selects.items():
        print((key, value))  # selects[i] = BooleanVar()里面的内容需要用value.get()获取，输出结果在下图

    def selectfunc():
        for key, value in selects.items():
            if value.get() == True:
                print(food[key])

    Button(root, text='提交', command=selectfunc).grid(row=len(food) + 2)
    root.mainloop()


class GpuInfo:
    gpuId = 0
    type = ""
    code = ""

    def __init__(self, gpuId, type, code):
        # 定义了两个实例变量
        self.gpuId = gpuId
        self.type = type
        self.code = code


if __name__ == '__main__':
    result = GpuInfo(1,"GPU","b").__dict__
    print(result)
    print(json.dumps(result,sort_keys=True, separators=(',', ':')))
    os.system('pause')