"""
Jetson Metrics Module

This module provides a class, JetsonMetrics, that facilitates monitoring of various system metrics on NVIDIA Jetson devices. 
It utilizes the jtop library to access real-time performance data including RAM usage, disk storage, and temperatures for CPU and GPU.

Dependencies:
    - jtop: Required for accessing Jetson hardware statistics. Install via pip using `pip install jetson-stats`.

Usage:
    ```python
    from jetson_metrics import JetsonMetrics

    if __name__ == '__main__':
        with JetsonMetrics() as metrics:
            all_metrics = metrics.get_all_metrics()
            for key, value in all_metrics.items():
                print(f"{key}: {value}")
    ```

    This will output:
    - RAM Usage (%)
    - Disk Storage Usage (%)
    - CPU Temperature (°C)
    - GPU Temperature (°C)

Note:
    Ensure that the `jtop` daemon is running on Jetson device (run `sudo jtop` if not already started) to enable access to the system metrics.

Author(s): Eddie, Sachit
Date: [Creation or Last Update Date]
"""
from jtop import jtop
import os

class JetsonMetrics:
    def __init__(self):
        self.jetson = jtop()
        self.jetson.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.jetson.close()

    def get_ram_usage_percentage(self):
        """ Returns the percentage of RAM used as an integer """
        ram = self.jetson.memory['RAM']
        return int((ram['used'] / ram['tot']) * 100) if ram['tot'] > 0 else 0

    def get_disk_storage_percentage(self):
        """ Returns the disk storage usage as a percentage of total disk space, rounded to the nearest integer """
        statvfs = os.statvfs('/')
        total = statvfs.f_blocks * statvfs.f_frsize
        free = statvfs.f_bfree * statvfs.f_frsize
        used = total - free
        disk_usage_percentage = (used / total) * 100 if total > 0 else 0
        return int(disk_usage_percentage)

    def get_cpu_temperature(self):
        """ Returns the CPU temperature rounded to the nearest integer, if available """
        temps = self.jetson.temperature
        return int(temps['cpu']['temp']) if 'cpu' in temps and temps['cpu']['online'] else None

    def get_gpu_temperature(self):
        """ Returns the GPU temperature rounded to the nearest integer, if available """
        temps = self.jetson.temperature
        return int(temps['gpu']['temp']) if 'gpu' in temps and temps['gpu']['online'] else None

    def close(self):
        """ Closes the jtop connection """
        self.jetson.close()

    def get_all_metrics(self):
        """ Returns all relevant metrics in a dictionary """
        return {
            "RAM Usage (%)": self.get_ram_usage_percentage(),
            "Disk Storage Usage (%)": self.get_disk_storage_percentage(),
            "CPU Temperature (°C)": self.get_cpu_temperature(),
            "GPU Temperature (°C)": self.get_gpu_temperature()
        }

# Usage
if __name__ == '__main__':
    with JetsonMetrics() as metrics:
        all_metrics = metrics.get_all_metrics()
        for key, value in all_metrics.items():
            print(f"{key}: {value}")
