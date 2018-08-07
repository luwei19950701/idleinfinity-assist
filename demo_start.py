# -*- coding: utf-8 -*-

# 使用说明
# python 3
# 下载谷歌浏览器
# 下载谷歌浏览器驱动，放入path路径下（注意给执行权限）
# 安装包 pip install selenium
# 命令行运行 python index.py
# 命令框输入验证码

import traceback
import datetime
from idle import Idle

name = "帐号"
pwd = "密码"
idle = Idle(name, pwd)
idle.start()
idle.character()

while True:
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')  # 当前时间
    print("========== 功能列表 ==========")
    print("==========1.通刷秘本==========")
    print("==========2.半刷秘本==========")
    print("==========3.Boss秘本==========")
    print("==========4.一键卖物==========")
    print("==========5.更换角色==========")
    print("==========6.退出程序==========")
    print("==== " + nowTime + " ====")

    number = input("选择功能：")
    if "1" == number:
        try:
            idle.mystery(1)
        except Exception as e:
            traceback.print_exc()
            continue

    elif "2" == number:
        try:
            idle.mystery(2)
        except Exception as e:
            traceback.print_exc()
            continue

    elif "3" == number:
        try:
            idle.mystery(3)
        except Exception as e:
            traceback.print_exc()
            continue

    elif "4" == number:
        idle.sell()

    elif "5" == number:
        idle.character()

    elif "6" == number:
        idle.quit()
        break

    else:
        print("未知的指令，重新输入...\n")
