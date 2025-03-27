import asyncio
import os
from importlib import resources
import logging
from tl_producer.fluent_sender.runner import SenderRunner



# Loads fluentbit


# Setup threads for different 'clients'
async def run():
    runners = [asyncio.create_task(SenderRunner(file)) for file in resources.files("tl_producer.data").iterdir()]

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.start_soon(runner.run()) for runner in runners]


# Thrreads send logs through fluentbit to defined endpoint
asyncio.run(run())