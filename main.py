#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import asyncio
import prometheus_client as prom
from pynvml import *
import random

format = "%(asctime)s - %(levelname)s [%(name)s] %(threadName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=format)

total_fb_memory = prom.Gauge('gpu_total_fb_memory_mb', 'Total installed frame buffer memory (in ''megabytes)', ['host', 'device'])
free_fb_memory = prom.Gauge('gpu_free_fb_memory_mb', 'Unallocated frame buffer memory (in ''megabytes)', ['host', 'device'])
used_fb_memory = prom.Gauge('gpu_used_fb_memory_mb', 'Allocated frame buffer memory (in megabytes).'' Note that the diver/GPU will always set ''a small amount of memory fore bookkeeping.', ['host', 'device'])
gpu_utilization = prom.Gauge('gpu_utilization_pct', 'Percent of time over the past sample period ''during which one or more kernels was ''executing on the GPU.', ['host', 'device'])
memory_utilization = prom.Gauge('gpu_mem_utilization_pct', 'Percent of time over the past sample ''period during which global (device) memory ''was being read or written', ['host', 'device'])

with open('/host/etc/hostname', 'r') as f:
    hostname = f.readline().strip()

async def compute_gpu_stat(gpu_id):
    handle = nvmlDeviceGetHandleByIndex(gpu_id)
    while True:
        mem_info = nvmlDeviceGetMemoryInfo(handle)
        logging.info('[%s/%d] Memory used: %s' % (hostname, gpu_id, str(mem_info.used)))
        total_fb_memory.labels(host=hostname, device=gpu_id).set(mem_info.total / 1024)
        free_fb_memory.labels(host=hostname, device=gpu_id).set(mem_info.free / 1024)
        used_fb_memory.labels(host=hostname, device=gpu_id).set(mem_info.used / 1024)

        utilization = nvmlDeviceGetUtilizationRates(handle)
        logging.info('[%s/%d] Utilization GPU: %s' % (hostname, gpu_id, str(utilization.gpu / 100.0)))
        gpu_utilization.labels(host=hostname, device=gpu_id).set(utilization.gpu / 100.0)
        memory_utilization.labels(host=hostname, device=gpu_id).set(utilization.memory / 100.0)

        sleep_time = random.random()
        await asyncio.sleep(sleep_time)


if __name__ == '__main__':

    nvmlInit()
    logging.info('Started with nVidia driver version = %s', nvmlSystemGetDriverVersion())
    device_count = nvmlDeviceGetCount()
    logging.info('%d devices found.', device_count)

    tasks = []
    loop = asyncio.get_event_loop()
    prom.start_http_server(9200)

    for i in range(device_count):
        tasks.append(loop.create_task(compute_gpu_stat(i)))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
