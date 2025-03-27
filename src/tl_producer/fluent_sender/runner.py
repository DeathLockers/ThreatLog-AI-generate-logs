import asyncio
import logging
from tl_producer.fluent_sender.sender import FluentSender

class SenderRunner():
    def __init__(self, config):
        self.config = config['runner']
        self.sender = FluentSender(config['fluent'])

    async def run(self):
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
        self.sender.stop()