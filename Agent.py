import psutil
import platform
import os
import time
import requests
import json

MASTER = '127.0.0.1:10086'


# 获取CPU信息
def get_cpu_info():
    cpu_info = {}
    cpu_info['CPU物理核心数'] = psutil.cpu_count(logical=False)
    cpu_info['CPU逻辑核心数'] = psutil.cpu_count(logical=True)
    cpu_info['CPU使用率'] = psutil.cpu_percent(interval=2)
    return cpu_info


# 获取内存信息
def get_memory_info():
    memory_info = {}
    memory = psutil.virtual_memory()
    memory_info['总内存'] = f"{round(memory.total/1024/1024/1024,2)}GB"
    memory_info['已用内存'] = f"{round(memory.used/1024/1024/1024,2)}GB"
    memory_info['空闲内存'] = f"{round(memory.free/1024/1024/1024,2)}GB"
    memory_info['内存使用率'] = f"{memory.percent}%"
    swap = psutil.swap_memory()
    memory_info['总交换空间'] = f"{round(swap.total/1024/1024/1024,2)}GB"
    memory_info['已用交换空间'] = f"{round(swap.used/1024/1024/1024,2)}GB"
    memory_info['空闲交换空间'] = f"{round(swap.free/1024/1024/1024,2)}GB"
    memory_info['交换空间使用率'] = f"{swap.percent}%"
    return memory_info


# 获取硬盘信息
def get_disk_info():
    disk_info = {}
    disks = psutil.disk_partitions()
    for disk in disks:
        mount_point = disk.mountpoint
        if os.name == 'nt':
            mount_point = mount_point.replace('\\', '/')
        usage = psutil.disk_usage(disk.mountpoint)
        disk_info[mount_point] = {}
        disk_info[mount_point]['总容量'] = f"{round(usage.total/1024/1024/1024,2)}GB"
        disk_info[mount_point]['已用容量'] = f"{round(usage.used/1024/1024/1024,2)}GB"
        disk_info[mount_point]['空闲容量'] = f"{round(usage.free/1024/1024/1024,2)}GB"
        disk_info[mount_point]['使用率'] = f"{usage.percent}%"
    return disk_info


# 获取网络信息
def get_network_info():
    network_info = {}
    network_io_counters1 = psutil.net_io_counters()
    time.sleep(1)
    network_io_counters2 = psutil.net_io_counters()
    network_sent = network_io_counters2.bytes_sent - network_io_counters1.bytes_sent
    network_recv = network_io_counters2.bytes_recv - network_io_counters1.bytes_recv
    total_bytes = network_sent + network_recv
    network_speed = 0
    for interface, stats in psutil.net_if_stats().items():
        if stats.isup:
            network_speed += stats.speed * 1024 * 1024
    network_info['网络利用率'] = f"{round(total_bytes / network_speed * 100, 2)}%"
    network_info['丢包率'] = f"{network_io_counters2.packets_sent - network_io_counters1.packets_sent}/{network_io_counters2.packets_sent}"
    return network_info


# 获取系统信息
def get_system_info():
    system_info = {}
    system_info['OS Name'] = platform.system()
    system_info['OS version'] = platform.version()
    system_info['OS Arch'] = platform.architecture()[0]
    system_info['Hostname'] = platform.node()
    return system_info


# 打印设备硬件数据
def print_hardware_info():
    print('CPU信息：')
    print(get_cpu_info())
    print('内存信息：')
    print(get_memory_info())
    print('硬盘信息：')
    print(get_disk_info())
    print('网络信息：')
    print(get_network_info())
    print('系统信息：')
    print(get_system_info())


# 报告设备运行状态
def report_hardware_info():
    print('Collecting Device Info...')
    info = {}
    info['CPU Usage'] = psutil.cpu_percent(interval=2)
    info['Memory Usage'] = f"{psutil.virtual_memory().percent}"
    info['Swap Usage'] = f"{psutil.swap_memory().percent}"
    disk_info = {}
    disks = psutil.disk_partitions()
    for disk in disks:
        mount_point = disk.mountpoint
        if os.name == 'nt':
            mount_point = mount_point.replace('\\', '/')
        usage = psutil.disk_usage(disk.mountpoint)
        disk_info[mount_point] = {}
        disk_info[mount_point]['Total'] = f"{round(usage.total/1024/1024/1024,2)}GB"
        disk_info[mount_point]['Used'] = f"{round(usage.used/1024/1024/1024,2)}GB"
        disk_info[mount_point]['Free'] = f"{round(usage.free/1024/1024/1024,2)}GB"
        disk_info[mount_point]['Disk Usage'] = f"{usage.percent}"
    info['Disk Usgae'] = disk_info
    network_io_counters1 = psutil.net_io_counters()
    time.sleep(1)
    network_io_counters2 = psutil.net_io_counters()
    network_sent = network_io_counters2.bytes_sent - network_io_counters1.bytes_sent
    network_recv = network_io_counters2.bytes_recv - network_io_counters1.bytes_recv
    total_bytes = network_sent + network_recv
    network_speed = 0
    for interface, stats in psutil.net_if_stats().items():
        if stats.isup:
            network_speed += stats.speed * 1024 * 1024
    info['Network Usage'] = f"{round(total_bytes / network_speed * 100, 2)}"
    info['Package Loss Rate'] = f"{round((network_io_counters2.dropin - network_io_counters1.dropin +network_io_counters2.dropout - network_io_counters1.dropout + network_io_counters2.errout - network_io_counters1.errout)/(network_io_counters2.packets_sent-network_io_counters1.packets_sent), 2)}"
    info['System Info'] = get_system_info()
    print('Collected!')
    headers = {'Content-Type':'application/json'}
    response = requests.post(url=MASTER, headers=headers, data=json.dumps(info))
    if response.status_code == 200:
        print('Successfully report system info to master node.')
    else:
        print('An error occurred when sending system info.')


if __name__ == '__main__':
    report_hardware_info()
