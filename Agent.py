import json
import os
import platform
import time

import psutil
import requests

MASTER = 'http://127.0.0.1:10086/report'


# 获取系统信息
def get_system_info():
    system_info = {}
    system_info['OS Name'] = platform.system()
    system_info['OS version'] = platform.version()
    system_info['OS Arch'] = platform.architecture()[0]
    system_info['Hostname'] = platform.node()
    return system_info


# 报告设备运行状态
def report_hardware_info():
    print('Collecting Infomation...')
    info = {}
    info['Time Stamp'] = time.time_ns()
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
    if network_io_counters2.packets_sent-network_io_counters1.packets_sent:
        info['Package Loss Rate'] = f"{round((network_io_counters2.dropin - network_io_counters1.dropin +network_io_counters2.dropout - network_io_counters1.dropout + network_io_counters2.errout - network_io_counters1.errout)/(network_io_counters2.packets_sent-network_io_counters1.packets_sent), 2)}"
    else:
        info['Package Loss Rate'] = 0.00
    info['System Info'] = get_system_info()
    print('Collected!')
    headers = {'Content-Type': 'application/json'}
    i = 0
    while i < 11:
        try:
            response = requests.post(
                url=MASTER, headers=headers, data=json.dumps(info))
            if response.status_code == 200:
                print('Successfully report system state to master node.')
                break
            else:
                print('An error occurred when sending system state.')
                print(f'We will try for {10-i} more time(s).')
                time.sleep(0.5)
        except:
            print('Network error! Unable to report system state.')
            print(f'We will try for {10-i} more time(s).')
            time.sleep(0.5)
        i += 1
    if i > 10:
        print('Failed to report system state.')
        print('system state collected as follows:')
        print(info)


if __name__ == '__main__':
    report_hardware_info()
