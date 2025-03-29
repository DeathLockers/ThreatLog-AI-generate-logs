import asyncio
import logging
from importlib import resources

from tl_producer.fluent_sender.runner import create_runner

# Loads fluentbit


# Setup threads for different 'clients'
async def run():
    """Run the main function."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting clients runners from files...")
    runners = [create_runner(file) for file in resources.files("tl_producer.data").iterdir()]

    async with asyncio.TaskGroup() as tg:
        try:
            for runner in runners:
                logging.info(f"Starting sender runner for file {runner.file}...")
                tg.create_task(runner.run())

            # tasks = [tg.create_task(runner.run()) for runner in runners]
            # asyncio.wait(tasks)
        except Exception as e:
            logging.error(f"Error in task group: {e}")

    logging.info("All tasks completed.")

# Thrreads send logs through fluentbit to defined endpoint
asyncio.run(run())
