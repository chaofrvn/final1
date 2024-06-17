from confluent_kafka import Consumer, KafkaError
import socket
import json

from mailjet_rest import Client
from dotenv import load_dotenv
import os

load_dotenv("../.env")
# Initialize the Kafka consumer with SASL_SSL authentication
consumer = Consumer(
    {
        "bootstrap.servers": "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": "HGLHHLIGH5YQYKVX",
        "sasl.password": "gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9",
        "group.id": "email",
        "auto.offset.reset": "latest",  # Start from the latest message
        "client.id": socket.gethostname(),
    }
)
API_KEY = os.environ["MJ_APIKEY_PUBLIC"]
API_SECRET = os.environ["MJ_APIKEY_PRIVATE"]
mailjet = Client(auth=(API_KEY, API_SECRET), version="v3.1")


def send_email(mailjet: Client, msg: str, email: str, user_id: str):
    if email is None:
        return
    data = {
        "Messages": [
            {
                "From": {"Email": "huyhoang123abcdef@gmail.com", "Name": "Stock"},
                "To": [{"Email": email, "Name": "Người dùng Discord " + user_id}],
                "Subject": "Cảnh báo chứng khoán",
                "TextPart": msg,
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print(result)
    print(result.json())


# Subscribe to the Kafka topic
consumer.subscribe(["stock_warning"])

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
            # Parse the received message
            # value = msg.value().decode('utf-8')
            # symbol, price = value.split(':')
            # push_data(json.load(msg.value()))\
            # print(type(msg.value()]))
            # push_data(type(msg.value().decode('utf-8')))
            data = json.loads(msg.value().decode("utf-8"))
            if data["msg"] is not None:
                send_email(
                    mailjet=mailjet,
                    msg=data["msg"],
                    email=data["email"],
                    user_id=str(msg.key()),
                )


except KeyboardInterrupt:
    pass
finally:
    # Close the consumer gracefully
    consumer.close()
