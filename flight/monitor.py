from jtop import jtop
import copy

#additional per cpu metrics user, nice, system utilization 
"""def cpu_metrics(metrics_requested = {'online', 'idle'}):
    jetson = jtop()
    jetson.start()
    compute_metrics = jetson.cpu
    jetson.close() 
    result = dict()
    result['total'] = dict()
    result['total'] = copy.copy(compute_metrics['total'])
    currCpuCount = 0
    for cpu_metrics in compute_metrics['cpu']:
        currCpuDict = f'cpu{currCpuCount}'
        result[currCpuDict] = dict()
        for metric in cpu_metrics:
            if metric in metrics_requested:
                result[currCpuDict][metric] = cpu_metrics[metric]
        currCpuCount += 1
    return result

#additional metrics min_freq, max_freq
def gpu_metrics(metrics_requested = {'load', 'curr_freq'}):
    result = dict()
    result['gpu'] = dict()
    jetson = jtop()
    jetson.start()
    gpu_metrics = jetson.gpu['gpu']
    freq_metrics = gpu_metrics['freq']
    jetson.close()
    if 'load' in metrics_requested:
        result['gpu'] = gpu_metrics['status']['load']
    if 'curr_freq' in metrics_requested:
        result['curr_freq'] = freq_metrics['cur']
    if 'min_freq' in metrics_requested:
        result['min_freq'] = freq_metrics['min']
    if 'max_freq' in metrics_requested:
        result['max_freq'] = freq_metrics['max']
    return result

#for RAM can have shared, used, buffers, cached
#temperature devices- cpu, gpu, soc1, soc2, soc0
def misc_metrics(ram_metrics_requested = {'tot', 'free'} , 
                temp_devices_requested = {'cpu', 'gpu', 'soc1', 'soc2', 'soc0'}):
    result = dict()
    jetson = jtop()
    jetson.start()
    ram_metrics = jetson.memory['RAM']
    temp_metrics = jetson.temperature
    jetson.close()
    result['RAM'] = dict()
    for metric in ram_metrics:
        if metric in ram_metrics_requested:
            result['RAM'][metric] = ram_metrics[metric]
    result['Temperature'] = dict()
    for device in temp_metrics:
        if temp_metrics[device]['online'] == False:
            continue
        if device in temp_devices_requested:
            result['Temperature'][device] = temp_metrics[device]['temp']
    return result

if __name__ == '__main__':
    print(cpu_metrics())
    print(gpu_metrics())
    print(misc_metrics())"""