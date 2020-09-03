# 代码块拷贝自https://github.com/yuban10703/IOTQQ-color_pic
import datetime
import time

from iotbot.decorators import equal_content
from iotbot.sugar import Text

try:
    import cpuinfo
    import psutil
except ImportError as e:
    raise Exception('请先安装依赖库：pip install py-cpuinfo, psutil') from e


def get_cpu_info():
    info = cpuinfo.get_cpu_info()  # 获取CPU型号等
    cpu_count = psutil.cpu_count(logical=False)  # 1代表单核CPU，2代表双核CPU
    xc_count = psutil.cpu_count()  # 线程数，如双核四线程
    cpu_percent = round((psutil.cpu_percent()), 2)  # cpu使用率
    try:
        model = info['hardware_raw']  # cpu型号
    except Exception:
        model = info['brand_raw']  # cpu型号
    try:  # 频率
        freq = info['hz_actual_friendly']
    except Exception:
        freq = 'null'
    cpu_info = (model, freq, info['arch'], cpu_count, xc_count, cpu_percent)
    return cpu_info


def get_memory_info():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    total_nc = round((float(memory.total) / 1024 / 1024 / 1024), 3)  # 总内存
    used_nc = round((float(memory.used) / 1024 / 1024 / 1024), 3)  # 已用内存
    available_nc = round((float(memory.available) / 1024 / 1024 / 1024), 3)  # 空闲内存
    percent_nc = memory.percent  # 内存使用率
    swap_total = round((float(swap.total) / 1024 / 1024 / 1024), 3)  # 总swap
    swap_used = round((float(swap.used) / 1024 / 1024 / 1024), 3)  # 已用swap
    swap_free = round((float(swap.free) / 1024 / 1024 / 1024), 3)  # 空闲swap
    swap_percent = swap.percent  # swap使用率
    men_info = (
        total_nc,
        used_nc,
        available_nc,
        percent_nc,
        swap_total,
        swap_used,
        swap_free,
        swap_percent,
    )
    return men_info


def uptime():
    now = time.time()
    boot = psutil.boot_time()
    boottime = datetime.datetime.fromtimestamp(boot).strftime("%Y-%m-%d %H:%M:%S")
    nowtime = datetime.datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")
    up_time = str(
        datetime.datetime.utcfromtimestamp(now).replace(microsecond=0)
        - datetime.datetime.utcfromtimestamp(boot).replace(microsecond=0)
    )
    alltime = (boottime, nowtime, up_time)
    return alltime


def sysinfo():
    cpu_info = get_cpu_info()
    mem_info = get_memory_info()
    up_time = uptime()
    msg = (
        'CPU型号:{0}\r\n频率:{1}\r\n架构:{2}\r\n核心数:{3}\r\n线程数:{4}\r\n负载:{5}%\r\n{6}\r\n'
        '总内存:{7}G\r\n已用内存:{8}G\r\n空闲内存:{9}G\r\n内存使用率:{10}%\r\n{6}\r\n'
        'swap:{11}G\r\n已用swap:{12}G\r\n空闲swap:{13}G\r\nswap使用率:{14}%\r\n{6}\r\n'
        '开机时间:{15}\r\n当前时间:{16}\r\n已运行时间:{17}'
    )
    full_meg = msg.format(
        cpu_info[0],
        cpu_info[1],
        cpu_info[2],
        cpu_info[3],
        cpu_info[4],
        cpu_info[5],
        '*' * 20,
        mem_info[0],
        mem_info[1],
        mem_info[2],
        mem_info[3],
        mem_info[4],
        mem_info[5],
        mem_info[6],
        mem_info[7],
        up_time[0],
        up_time[1],
        up_time[2],
    )
    return full_meg


@equal_content('sysinfo')
def receive_group_msg(_):
    Text(sysinfo())


@equal_content('sysinfo')
def receive_friend_msg(_):
    Text(sysinfo())
