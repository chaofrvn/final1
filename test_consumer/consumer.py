from confluent_kafka import Consumer, KafkaError
import socket
from influx_db import push_data
import json

# Initialize the Kafka consumer with SASL_SSL authentication
consumer = Consumer(
    {
        "bootstrap.servers": "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": "HGLHHLIGH5YQYKVX",
        "sasl.password": "gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9",
        "group.id": "stock_price_group",
        "auto.offset.reset": "latest",  # Start from the latest message
        "client.id": socket.gethostname(),
    }
)

# Subscribe to the Kafka topic
consumer.subscribe(["stockPrice"])

try:
    while True:
        msg = consumer.poll(10)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error while consuming: {msg.error()}")
        else:

            push_data(json.loads(msg.value().decode("utf-8")))


except KeyboardInterrupt:
    pass
finally:
    # Close the consumer gracefully
    consumer.close()
