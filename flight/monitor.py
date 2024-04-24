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
        return int(temps['cpu']['temp']) if 'cpu' in temps and temps['cpu']['online'] else None

    def close(self):
        """ Closes the jtop connection """
        self.jetson.close()

# Usage
if __name__ == '__main__':
    with JetsonMetrics() as metrics:
        print("RAM Usage (%):", metrics.get_ram_usage_percentage())
        print("Disk Storage Usage (%):", metrics.get_disk_storage_percentage())
        print("CPU Temperature (°C):", metrics.get_cpu_temperature())
        print("GPU Temperature (°C):", metrics.get_gpu_temperature())
