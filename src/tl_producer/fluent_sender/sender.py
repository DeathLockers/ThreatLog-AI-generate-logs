import json
import logging
import os
from kafka import KafkaProducer

class KafkaSender:
    """KafkaSender is a class that sends messages to a Kafka topic.
    It uses the KafkaProducer from the kafka-python library to send messages.
    The class is initialized with a client_id and optional configuration parameters.
    https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
    Kafka parameters are readed from environment variables.
    """
    def __init__(self, client_id, **kwargs):
        self.topic = 'customoer_logs'
        self.kafka_config = KafkaConfig()
        self.kafka_config.set_key('client_id', client_id)
        if isinstance(kwargs, dict) or isinstance(kwargs, set):
            if 'value_serializer' in kwargs:
                self.kafka_config.set_key('value_serializer', kwargs['value_serializer'])


    def send(self, trace:str):
        """Send a trace to the Kafka topic.
        Args:
            trace (str): The trace to send.
        """
        self.setup()
        logging.info(f"Sending trace to Kafka topic {self.topic}: {trace}")
        self.producer.send(self.topic, trace)

    def setup(self):
        """Setup the Kafka producer.
        This method initializes the Kafka producer with the configuration parameters."""
        if self.producer is not None:
            return
        logging.info("Kafka producer is not initialized. Initializing...")
        self.producer = KafkaProducer(**self.kafka_config.args)

    def stop(self):
        """Stop the Kafka producer.
        This method flushes and closes the Kafka producer."""
        if self.producer is None:
            return
        logging.info("Stopping Kafka producer...")
        self.producer.flush()
        self.producer.close()
        self.producer = None

 
class KafkaConfig:
    """KafkaConfig is a class that holds the configuration parameters for the Kafka producer.
    It reads the parameters from environment variables.
    The class is initialized with the following parameters:
    - bootstrap_servers: The Kafka broker address.
    - acks: The number of acknowledgments the producer requires the leader to have received before considering a request complete.
    - value_serializer: The serializer for the value of the message.
    - security_protocol: The protocol used to communicate with the broker.
    - sasl_plain_username: The username for SASL authentication.
    - sasl_plain_password: The password for SASL authentication.
    """
    args = {}
    KOWN_SECURITY_PROTOCOLS = ['PLAINTEXT','SASL_SSL']

    def __init__(self):
        self.set_key('bootstrap_servers', os.environ.get('KAFKA_HOST'))
        self.set_key('acks', os.environ.get('KAFKA_ACKS'))
        self.set_key('value_serializer', lambda v: json.dumps(v).encode('utf-8'))
        security_protocol = os.environ.get('security_protocol', None)
        if security_protocol:
            security_protocol = self.security_protocol.lower()
            if security_protocol not in self.KOWN_SECURITY_PROTOCOLS:
                raise ValueError(f"Invalid security protocol: {self.security_protocol}. Must be one of {self.KOWN_SECURITY_PROTOCOLS}")
            
            self.set_key('security_protocol', security_protocol)
            if security_protocol == 'SASL_SSL':
                self.set_key('sasl_plain_username',os.environ.get('KAFFKA_USER'))
                self.set_key('sasl_plain_password',os.environ.get('KAFFKA_PASSWORD'))
                self.user = os.environ.get('KAFFKA_PASSWORD')
    
    def set_key(self, key, value):
        """Set a key-value pair in the configuration dictionary.
        If the value is None, raise a ValueError."""
        if value:
            self.args[key] = value
        else:
            raise ValueError(f"Missing required environment variable: {key}")