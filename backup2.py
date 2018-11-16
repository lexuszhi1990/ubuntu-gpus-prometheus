#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://www.forwardingflows.net/asyncio_python_prometheus_gauge_example/


import asyncio
import prometheus_client as prom
import logging
import random
format = "%(asctime)s - %(levelname)s [%(name)s] %(threadName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=format)
g1 = prom.Gauge('compute_gauge_rate', 'Random gauge', labelnames=['task_name'])
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
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Start up the server to expose metrics.
    prom.start_http_server(8000)
    t0_value = 50
    tasks = [loop.create_task(compute_rate('x', rate=t0_value)),
             loop.create_task(compute_rate('y', rate=t0_value/2))]
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
