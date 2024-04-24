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

    def get_disk_storage(self):
        """ Returns the disk storage usage as (total, used, free) in GB, rounded to the nearest integer """
        statvfs = os.statvfs('/')
        total = int((statvfs.f_blocks * statvfs.f_frsize) / (1024 ** 3))
        free = int((statvfs.f_bfree * statvfs.f_frsize) / (1024 ** 3))
        used = total - free
        return (total, used, free)

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

# Usage
if __name__ == '__main__':
    with JetsonMetrics() as metrics:
        print("RAM Usage (%):", metrics.get_ram_usage_percentage())
        total, used, free = metrics.get_disk_storage()
        print("Disk Storage (GB) - Total: {}, Used: {}, Free: {}".format(total, used, free))
        print("CPU Temperature (°C):", metrics.get_cpu_temperature())
        print("GPU Temperature (°C):", metrics.get_gpu_temperature())
