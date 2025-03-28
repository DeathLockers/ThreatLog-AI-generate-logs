import asyncio
import logging
from tl_producer.fluent_sender.sender import KafkaSender

class SenderRunner():
    def __init__(self, config):
        self.config = config['runner']
        self.sender = KafkaSender(config['client_id'])

    async def run(self):
        """Run the sender in an asynchronous loop"""
        logging.info(f"Starting sender {self.config['client_id']}...")
        try:
            self.sender.start()
            while True:
                try:
                    with open(self.config['file'], 'r') as file:
                        while (line:=file.readline()):
                            self.sender.send(line)
                            await asyncio.sleep(self.config['interval'])
                except Exception as e:
                    print(e)
                    continue
                await asyncio.sleep(self.config['interval'])
        except Exception as e:
            logging.error(f"Error initializing sender: {e}")

    def stop(self):
        """Stop the sender gracefully"""
        logging.info(f"Stopping sender {self.config['client_id']}...")
        self.sender.stop()