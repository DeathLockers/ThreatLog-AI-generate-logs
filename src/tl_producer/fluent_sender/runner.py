import asyncio
import logging
import os
from tl_producer.fluent_sender.sender import KafkaSender

class SenderRunner():
    def __init__(self, config):
        self.file = config['runner']['filePath']
        self.interval = config['runner']['interval']
        self.client_id = config['client_id']
        self.sender = KafkaSender(self.client_id)

    async def run(self):
        """Run the sender in an asynchronous loop"""
        logging.info(f"Starting sender {self.client_id}...")
        try:
            self.sender.setup()
            while True:
                try:
                    with open(self.file, 'r') as file:
                        while (line:=file.readline()):
                            self.sender.send(line)
                            await asyncio.sleep(self.interval)
                except Exception as e:
                    print(e)
                    continue
                await asyncio.sleep(self.interval)
        except Exception as e:
            logging.error(f"Error initializing sender: {e}", e)

    def stop(self):
        """Stop the sender gracefully"""
        logging.info(f"Stopping sender {self.client_id}...")
        self.sender.stop()

def create_runner(file)->SenderRunner:
    """Create a sender runner"""
    logging.info(f"Creating sender runner for file {file}...")
    if not file:
        raise ValueError("File path is required")
    
    client_id = extract_client(file)
    if not client_id:
        raise ValueError("Client ID is required")

    return SenderRunner({'runner':{'filePath':file, 'interval': os.getenv('RUNNER_INTERVAL_SECONDS', 5)}, 'client_id': client_id})


def extract_client(file) -> str:
    """Extract the client ID from the file name"""
    if not file:
        raise ValueError("File path is required")
    
    # Extract the client ID from the file name
    client_id = os.path.basename(file).split('.')[0].split('_')[-1]
    return client_id if client_id else None