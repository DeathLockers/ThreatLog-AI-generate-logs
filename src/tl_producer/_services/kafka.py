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

    initialized = False
    producer = None
    client_id = None

    def __init__(self, client_id, **kwargs):
        self.topic = "customer_logs"
        self.kafka_config = KafkaConfig()
        self.client_id = client_id
        if isinstance(kwargs, dict) or isinstance(kwargs, set):
            if "value_serializer" in kwargs:
                self.kafka_config.set_key("value_serializer", kwargs["value_serializer"])

    def send(self, trace: str):
        """Send a trace to the Kafka topic.
        Args:
            trace (str): The trace to send.
        """
        logging.info("Sending trace to Kafka topic %s: %s", self.topic, trace)

        if not self.initialized:
            raise ValueError("Kafka producer is not initialized. Call setup() before sending messages.")
        self.producer.send(self.topic, {"trace": trace, "client_id": self.client_id})

    def setup(self):
        """Setup the Kafka producer.
        This method initializes the Kafka producer with the configuration parameters."""
        if self.producer is not None:
            return

        logging.info("Kafka producer is not initialized. Initializing...")
        self.producer = KafkaProducer(**self.kafka_config.args)
        self.initialized = True

    def stop(self):
        """Stop the Kafka producer.
        This method flushes and closes the Kafka producer."""
        if self.producer is None:
            return
        logging.info("Stopping Kafka producer...")
        try:
            self.producer.flush()
            self.producer.close()
        except Exception as e:
            logging.error("Error stopping Kafka producer: %s", e)
        self.producer = None


class KafkaConfig:
    """KafkaConfig is a class that holds the configuration parameters for the Kafka producer.
    It reads the parameters from environment variables.
    The class is initialized with the following parameters extracted from os environment variables:
    - bootstrap_servers: The Kafka broker address. KAFK_HOST
    - acks: The number of acknowledgments the producer requires the leader to have received before
            considering a request complete. KAFKA_ACKS
        - 1 means the leader will write the record to its local log but will respond without
            awaiting full acknowledgement from all followers.
        - 0 means the leader will not wait for any acknowledgment from the broker.
        - -1 means the leader will block until all in-sync replicas have acknowledged the record.
    - value_serializer: The serializer for the value of the message. Default is json.dumps.
    - security_protocol: The protocol used to communicate with the broker. Default is PLAINTEXT.
    - sasl_plain_username: The username for SASL authentication. KAFFKA_USER
    - sasl_plain_password: The password for SASL authentication. KAFFKA_PASSWORD
    """

    args = {}
    KOWN_SECURITY_PROTOCOLS = ["PLAINTEXT", "SASL_SSL"]

    def __init__(self):
        self.set_key("bootstrap_servers", self._get("KAFKA_HOST", "broker:9093"))
        self.set_key("acks", self._get("KAFKA_ACKS", 1))
        self.set_key("value_serializer", lambda v: json.dumps(v).encode("utf-8"))
        security_protocol = self._get("security_protocol", "PLAINTEXT")
        if security_protocol:
            security_protocol = security_protocol.upper()
            if security_protocol not in self.KOWN_SECURITY_PROTOCOLS:
                raise ValueError(f"Invalid security protocol: {security_protocol}. Must be one of {self.KOWN_SECURITY_PROTOCOLS}")

            self.set_key("security_protocol", security_protocol)
            if security_protocol == "SASL_SSL":
                self.set_key("sasl_plain_username", self._get("KAFKA_USER"))
                self.set_key("sasl_plain_password", self._get("KAFKA_PASSWORD"))
                self.user = self._get("KAFKA_PASSWORD")

    def set_key(self, key, value):
        """Set a key-value pair in the configuration dictionary.
        If the value is None, raise a ValueError."""
        logging.info("Setting %s to %s", key, value)
        if value:
            self.args[key] = value

    def _get(self, key, default=None, raise_if_missing=False):
        """Get the value of a key from the environment variables."""
        value = os.environ.get(key, default)
        if raise_if_missing and value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
