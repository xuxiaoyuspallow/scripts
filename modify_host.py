'''
防止我沉迷b站，每隔一小时写一次host，阻断b站流量

需要对hosts文件进行权限修改，右键hosts文件，属性->安全->高级->权限->添加， 添加一个当前用户可以写入的权限

再在任务周期那里，设置开机启动此脚本
'''

import schedule
import time


# Keep the program running indefinitely
def modify_host():
    host_path = "C:\Windows\System32\drivers\etc\hosts"
    to_write_hosts = [
        "127.0.0.1 www.bilibili.com"
    ]
    with open(host_path,"r+") as f:
        content = f.read()
        for line in to_write_hosts:
            if line not in content:
                f.write("\n" + line+ "\n")
            elif ("#" + line) in f.read():
                f.write("\n" + line+ "\n")

modify_host()
schedule.every().hour.do(modify_host)


while True:
    schedule.run_pending()
    time.sleep(1)
