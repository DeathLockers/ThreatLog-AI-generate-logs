import asyncio
import logging
import os

import anyio

from tl_producer._services.kafka import KafkaSender


class SenderRunner:
    """
    Clase encargada de gestionar el envío de trazas a Kafka
    """

    def __init__(self, config):
        self.file = config["runner"]["filePath"]
        if not self.file:
            raise ValueError("File path is required")

        if not os.path.exists(self.file):
            raise ValueError("File %s does not exist", self.file)

        self.interval = config["runner"]["interval"]
        self.client_id = config["client_id"]
        self.sender = KafkaSender(self.client_id)

    async def run(self):
        """Run the sender in an asynchronous loop"""
        logging.info("Starting sender %s...", self.client_id)
        try:
            self.sender.setup()
            while True:
                try:
                    async with await anyio.open_file(self.file) as file:
                        while line := await file.readline():
                            self.sender.send(line)
                            await asyncio.sleep(self.interval)
                except Exception as e:
                    logging.error("Error: %s while processing file messages", e)
                    continue
                await asyncio.sleep(self.interval * 10)
        except Exception as e:
            logging.error("Error initializing sender: %s", e)

    def stop(self):
        """Stop the sender gracefully"""
        logging.info("Stopping sender %s...", self.client_id)
        self.sender.stop()


def create_runner(file) -> SenderRunner:
    """Create a sender runner"""
    logging.info("Creating sender runner for file %s...", file)
    if not file:
        raise ValueError("File path is required")

    client_id = extract_client(file)
    if not client_id:
        raise ValueError("Client ID is required")

    return SenderRunner(
        {"runner": {"filePath": file, "interval": int(os.getenv("RUNNER_INTERVAL_SECONDS", 5))}, "client_id": client_id}
    )


def extract_client(file) -> str:
    """Extract the client ID from the file name"""
    if not file:
        raise ValueError("File path is required")

    # Extract the client ID from the file name
    client_id = os.path.basename(file).split(".")[0].split("_")[-1]
    return client_id if client_id else None
