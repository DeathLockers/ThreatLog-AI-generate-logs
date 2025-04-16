
import asyncio
import logging
import os
import pathlib
import sys

from dotenv import load_dotenv

if not __package__:
    """https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/#running-a-command-line-interface-from-source-with-src-layout"""
    # Make CLI runnable from source tree with
    #    python src/package
    package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, package_source_path)

load_dotenv()


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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Starting clients runners from files...")

    files_path = pathlib.Path(os.environ.get("RUNNER_FILES_PATH", "/data"))
    files = [f.name for f in files_path.iterdir() if f.is_file()]
    runners = [create_runner(file) for file in files]

    async with asyncio.TaskGroup() as tg:
        try:
            for runner in runners:
                logging.info("Starting sender runner for file %s...", runner.file)
                tg.create_task(runner.run())
        except Exception as e:
            logging.error("Error in task group: %s", e)

    logging.info("All tasks completed.")

if __name__ == "__main__":
    from tl_producer._services.runner import create_runner

    # Thrreads send logs through fluentbit to defined endpoint
    asyncio.run(run())
