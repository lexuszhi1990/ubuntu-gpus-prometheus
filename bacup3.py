#!/usr/bin/env python
# -*- coding: utf-8 -*-

import prometheus_client as prom
import pynvml
import logging
import time

format = "%(asctime)s - %(levelname)s [%(name)s] %(threadName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=format)

total_fb_memory = prom.Gauge('gpu_total_fb_memory_mb', 'Total installed frame buffer memory (in ''megabytes)', ['host', 'device'])
free_fb_memory = prom.Gauge('gpu_free_fb_memory_mb', 'Unallocated frame buffer memory (in ''megabytes)', ['host', 'device'])
used_fb_memory = prom.Gauge('gpu_used_fb_memory_mb', 'Allocated frame buffer memory (in megabytes).'' Note that the diver/GPU will always set ''a small amount of memory fore bookkeeping.', ['host', 'device'])
gpu_utilization = prom.Gauge('gpu_utilization_pct', 'Percent of time over the past sample period ''during which one or more kernels was ''executing on the GPU.', ['host', 'device'])
memory_utilization = prom.Gauge('gpu_mem_utilization_pct', 'Percent of time over the past sample ''period during which global (device) memory ''was being read or written', ['host', 'device'])

hostname = 'train22'

pynvml.nvmlInit()
print('Started with nVidia driver version = %s', pynvml.nvmlSystemGetDriverVersion())
device_count = pynvml.nvmlDeviceGetCount()

prom.start_http_server(9200)

while True:
    for i in range(device_count):
        print('Analyzing device %d...', i)

        handle = pynvml.nvmlDeviceGetHandleByIndex(i)

        print('Querying for memory information...')
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        total_fb_memory.labels(host=hostname, device=i).set(mem_info.total / 1024)
        free_fb_memory.labels(host=hostname, device=i).set(mem_info.free / 1024)
        used_fb_memory.labels(host=hostname, device=i).set(mem_info.used / 1024)

        print('Obtaining utilization statistics...')
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

        gpu_utilization.labels(host=hostname, device=i).set(utilization.gpu / 100.0)
        memory_utilization.labels(host=hostname, device=i).set(utilization.memory / 100.0)
        print('Gpu utilization = %s', utilization.gpu)
        print('Memory utilization = %s', utilization.memory)

        time.sleep(0.01)


# handle = pynvml.nvmlDeviceGetHandleByIndex(0)
# mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
# print('Memory information = %s', str(mem_info))
# total_fb_memory.labels(host=hostname, device=gpu_id).set(mem_info.total / 1e9)
# free_fb_memory.labels(host=hostname, device=gpu_id).set(mem_info.free / 1e9)
# used_fb_memory.labels(host=hostname, device=gpu_id).set(mem_info.used / 1e9)

# utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
# print('Utilization statistics = %s', str(utilization))
# gpu_utilization.labels(host=hostname, device=gpu_id).set(utilization.gpu / 100.0)
# memory_utilization.labels(host=hostname, device=gpu_id).set(utilization.memory / 100.0)

