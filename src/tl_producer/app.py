import asyncio
import logging
from importlib import resources
import os

from tl_producer.runner import create_runner

# Setup threads for different 'clients'
async def run():
    """
    Carga los archivos de logs de los distintos clientes y los envía a kafka en paralelo.
    Crea un hilo por cada cliente.
    Los archivos de logs se encuentran en la carpeta tl_producer/data.
    Si se define la variable de entorno RUNNER_FILES, se cargan los archivos de logs de los clientes definidos en la variable.
        *  La ruta de los archivos debe ser absoluta.
        *  Separa los archivos por '|'.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting clients runners from files...")
    files = resources.files("tl_producer.data").iterdir() if os.environ.get('RUNNER_FILES') is None else os.environ.get('RUNNER_FILES').split('|')
    runners = [create_runner(file) for file in files]

    async with asyncio.TaskGroup() as tg:
        try:
            for runner in runners:
                logging.info(f"Starting sender runner for file {runner.file}...")
                tg.create_task(runner.run())
        except Exception as e:
            logging.error(f"Error in task group: {e}")

    logging.info("All tasks completed.")

# Thrreads send logs through fluentbit to defined endpoint
asyncio.run(run())
