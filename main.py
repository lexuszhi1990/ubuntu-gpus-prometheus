#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import asyncio
import prometheus_client as prom
from pynvml import *


format = "%(asctime)s - %(levelname)s [%(name)s] %(threadName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=format)

total_fb_memory = Gauge('gpu_total_fb_memory_mb', 'Total installed frame buffer memory (in ''megabytes)', ['device'])
free_fb_memory = Gauge('gpu_free_fb_memory_mb', 'Unallocated frame buffer memory (in ''megabytes)', ['device'])
used_fb_memory = Gauge('gpu_used_fb_memory_mb', 'Allocated frame buffer memory (in megabytes).'' Note that the diver/GPU will always set ''a small amount of memory fore bookkeeping.', ['device'])
gpu_utilization = Gauge('gpu_utilization_pct', 'Percent of time over the past sample period ''during which one or more kernels was ''executing on the GPU.', ['device'])
memory_utilization = Gauge('gpu_mem_utilization_pct', 'Percent of time over the past sample ''period during which global (device) memory ''was being read or written', ['device'])

async def compute_rate(name, rate, delta_min=-100, delta_max=100):
    """Increases or decreases a rate based on a random delta value
    which varies from "delta_min" to "delta_max".
    :name: task_id
    :rate: initial rate value
    :delta_min: lowest delta variation
    :delta_max: highest delta variation
    """
    while True:
        logging.info("name: {} value {}".format(name, rate))
        g1.labels(task_name=name).set(rate)
        rate += random.randint(delta_min, delta_max)
        await asyncio.sleep(1)

async def compute_gpu_stat(gpu_id):
    handle = nvmlDeviceGetHandleByIndex(gpu_id)
    while True:
        utilization = nvmlDeviceGetUtilizationRates(handle)
        g1.labels(task_name='zs').set(utilization.gpu / 100.0)

        await asyncio.sleep(1)


if __name__ == '__main__':

    nvmlInit()
    logging.info('Started with nVidia driver version = %s', nvmlSystemGetDriverVersion())
    device_count = nvmlDeviceGetCount()
    logging.info('%d devices found.', device_count)

    loop = asyncio.get_event_loop()

    # Start up the server to expose metrics.
    prom.start_http_server(9200)
    t0_value = 50
    tasks = [loop.create_task(compute_gpu_stat(0)), loop.create_task(compute_gpu_stat(1))
             ]
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
