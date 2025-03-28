import json
import os
from kafka import KafkaProducer

class KafkaSender:
    def __init__(self, client_id, **kwargs):
        self.topic = 'customoer_logs'
        self.kafka_config = KafkaConfig()
        self.kafka_config.set_key('client_id', client_id)
        if isinstance(kwargs, dict) or isinstance(kwargs, set):
            if 'value_serializer' in kwargs:
                self.kafka_config.set_key('value_serializer', kwargs['value_serializer'])


    def send(self, trace):
        self.setup()

        self.producer.send(self.topic, trace)

    def setup(self):
        if self.producer is not None:
            return
        
        self.producer = KafkaProducer(**self.kafka_config.args)

    def stop(self):
        if self.producer is None:
            return
        
        self.producer.flush()
        self.producer.close()
        self.producer = None


class KafkaConfig:
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
        if value:
            self.args[key] = value
        else:
            raise ValueError(f"Missing required environment variable: {key}")