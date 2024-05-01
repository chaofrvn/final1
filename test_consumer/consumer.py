from confluent_kafka import Consumer, KafkaError
import socket
from influx_db import push_data
import json
# Initialize the Kafka consumer with SASL_SSL authentication
consumer = Consumer({'bootstrap.servers': 'pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'MPT6ORJOO7EOIBBT',
        'sasl.password': '/NjGhfqfDTWlLmh2d5iUeKdqz6Bm9POPBEH8S9fv0BiRsIXGmn68CYqPI1lfiOUA',
        'group.id': 'stock_price_group',
        'auto.offset.reset': 'latest',  # Start from the latest message
        'client.id': socket.gethostname()})

# Subscribe to the Kafka topic
consumer.subscribe(['topic_0'])

try:
    while True:
        msg = consumer.poll(10)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f'Error while consuming: {msg.error()}')
        else:
            # Parse the received message
            # value = msg.value().decode('utf-8')
            # symbol, price = value.split(':')
            # push_data(json.load(msg.value()))\
            # print(type(msg.value()]))
            # push_data(type(msg.value().decode('utf-8')))
            push_data(json.loads(msg.value().decode('utf-8')))
            print(json.loads(msg.value().decode('utf-8')))

except KeyboardInterrupt:
    pass
finally:
    # Close the consumer gracefully
    consumer.close()