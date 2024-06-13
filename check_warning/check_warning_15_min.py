import socket
from get_value import get_value
import operator
from bson import ObjectId
from confluent_kafka import Producer
import pandas as pd
from prefect import flow, task, get_run_logger
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo import UpdateOne
import asyncio
from mailjet_rest import Client
from influxdb_client import InfluxDBClient

import json

# logging.basicConfig(filename="logging.log",
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     filemode='w')

# # Creating an object
# logger = logging.getLogger()

load_dotenv("../.env")
conf = {
    "bootstrap.servers": "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "HGLHHLIGH5YQYKVX",
    "sasl.password": "gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9",
    "client.id": socket.gethostname(),
}
producer = Producer(conf)
KAFKA_TOPIC = "stock_warning"
uri = os.environ["MONGODB_URL"]
INFLUXDB_TOKEN = os.environ["INFLUXDB_TOKEN"]
client = MongoClient(host=uri)
database = client["finalProject"]
warningCollection = database["warning"]
org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient(url=host, token=INFLUXDB_TOKEN, org=org)
database = "stock_data"
query_api = client.query_api()


def delivery_report(err, msg, logger):
    if err is not None:
        logger.error("Message delivery failed: {}".format(err))
    else:
        logger.info("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


def send_to_kafka(producer: Producer, topic, key, message, logger):
    # Sending a message to Kafka
    # print(type(message))
    producer.produce(
        topic,
        key=key,
        value=message,
        callback=lambda err, msg: delivery_report(err=err, msg=msg, logger=logger),
    )
    producer.flush()


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


@task
def getWarning():
    # warnings = list(warningCollection.find({"is_15_minute": True}))
    # print(f"Receive {len(warnings)} 15 minute warnings")
    # return warnings
    pipeline = [
        {"$unwind": "$warnings"},  # Deconstruct the warnings array
        {
            "$match": {"warnings.is_15_minute": True}
        },  # Filter warnings with is_15_minute set to True
        {"$addFields": {"warnings.user_id": "$user_id", "warnings.email": "$email"}},
        {
            "$replaceRoot": {"newRoot": "$warnings"}
        },  # Replace the root document with the warnings
    ]
    result = list(warningCollection.aggregate(pipeline))
    print(result)
    return result


@task
def checkWarning(warnings):
    # first value is trigger, second value is is_greater
    comparison_funcs = {
        (True, True): operator.ge,  # trigger is True and is_greater is True (>=)
        (True, False): operator.le,  # trigger is True and is_greater is False (<=)
        (False, True): operator.lt,  # trigger is False and is_greater is True (<)
        (False, False): operator.gt,  # trigger is False and is_greater is False (>)
    }
    datas = {}
    df = pd.DataFrame()

    for warning in warnings:
        data = None
        if warning["ticker"] in datas:
            data = datas[warning["ticker"]]
        else:
            query = f"""from(bucket: "stock_data")
        |> range(start:0)
        |> filter(fn: (r) => r.ticker == "{warning["ticker"]}" and r._measurement=="{"stock_price" if warning["is_15_minute"]else "stock_daily"}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """
            data = query_api.query_data_frame(query=query, data_frame_index=["_time"])
            datas[warning["ticker"]] = data
            # print(data.index)

        value: pd.DataFrame = get_value(
            df=data,
            indicator=warning["indicator"],
            field=warning["field"],
            period=warning["period"],
        )
        if value is None:
            continue
        comparison_func = comparison_funcs[(warning["trigger"], warning["is_greater"])]
        if comparison_func(value["value"][0], warning["thresold"]):
            row = pd.DataFrame(
                {
                    "value": [value["value"][0]],
                    "trigger": warning["trigger"],
                    "ticker": warning["ticker"],
                    "user_id": warning["user_id"],
                    "thresold": warning["thresold"],
                    "field": warning["field"],
                    "indicator": warning["indicator"],
                    "id": warning["_id"],
                    "email": warning["email"],
                },
                index=[
                    value.index[0]
                    .tz_convert("Asia/Ho_Chi_Minh")
                    .strftime(
                        "%Y-%m-%d %H:%M:%S" if warning["is_15_minute"] else "%Y-%m-%d"
                    )
                ],
            )
            df = pd.concat([df, row])
    df.index.name = "_time"
    # print("\n"+df.to_markdown(tablefmt="grid"))
    return df


@task
def generate_message(warnings: pd.DataFrame):
    msg = pd.DataFrame()
    if len(warnings) > 0:
        warnings = warnings.round({"value": 3})
    for time, warning in warnings.iterrows():
        value = ""
        if warning["trigger"]:
            if warning["indicator"] is None:
                value = f'Cảnh báo: Giá trị {warning["field"]} của mã cổ phiếu {warning["ticker"]} đã quá ngưỡng cho phép là {warning["thresold"]}. Giá trị tại thời điểm {time} là {warning["value"]}'

            elif warning["indicator"] in ["rsi", "stoch_k", "stoch_d"]:
                value = f'Cảnh báo: Giá trị {warning["indicator"]} của mã cổ phiếu {warning["ticker"]} đã quá ngưỡng cho phép là {warning["thresold"]}. Giá trị tại thời điểm {time} là {warning["value"]}'
            else:
                value = f'Cảnh báo: Giá trị {warning["indicator"]} của trường {warning["field"]} của mã cổ phiếu {warning["ticker"]} đã quá ngưỡng cho phép là {warning["thresold"]}. Giá trị tại thời điểm {time} là {warning["value"]}'
        else:
            if warning["indicator"] is None:
                value = f'Giá trị {warning["field"]} của mã cổ phiếu {warning["ticker"]} đã về mức cho phép là {warning["thresold"]}. Giá trị tại thời điểm {time} là {warning["value"]}'
            elif warning["indicator"] in ["rsi", "stoch_k", "stoch_d"]:
                value = f'Giá trị {warning["indicator"]} của mã cổ phiếu {warning["ticker"]} đã về mức cho phép là {warning["thresold"]}. Giá trị tại thời điểm {time} là {warning["value"]}'
            else:
                value = f'Giá trị {warning["indicator"]} của trường {warning["field"]} của mã cổ phiếu {warning["ticker"]} đã về mức cho phép là {warning["thresold"]}. Giá trị tại thời điểm {time} là {warning["value"]}'
        msg = pd.concat(
            [
                msg,
                pd.DataFrame(
                    data={"msg": value, "email": warning["email"]},
                    index=[warning["user_id"]],
                ),
            ]
        )
    msg.index.name = "user_id"
    # print("\n"+msg.to_string())

    return msg


@task
def trigger_trigger(warnings):
    if "id" not in warnings.columns:
        return

    operations = []

    # Retrieve the documents containing the warnings
    documents = warningCollection.find({"warnings._id": {"$in": list(warnings["id"])}})

    for document in documents:
        for warning in document.get("warnings", []):
            if warning["_id"] in list(warnings["id"]):
                # Toggle the trigger field
                warning["trigger"] = not warning["trigger"]

        # Create an update operation
        operations.append(
            UpdateOne(
                {"_id": document["_id"]}, {"$set": {"warnings": document["warnings"]}}
            )
        )

    # Execute the bulk update
    if operations:
        result = warningCollection.bulk_write(operations, ordered=False)
        return result.bulk_api_result
    return None


@task
def send_message(msg: pd.DataFrame):
    logger = get_run_logger()
    for user_id, row in msg.iterrows():
        send_to_kafka(
            producer=producer,
            topic=KAFKA_TOPIC,
            key=str(user_id),
            message=row["msg"],
            logger=logger,
        )


@task
def send_emails(msg: pd.DataFrame):
    API_KEY = os.environ["MJ_APIKEY_PUBLIC"]
    API_SECRET = os.environ["MJ_APIKEY_PRIVATE"]

    mailjet = Client(auth=(API_KEY, API_SECRET), version="v3.1")
    for user_id, row in msg.iterrows():
        # thêm email
        send_email(mailjet, row["msg"], row["email"], str(user_id))

    return


@flow(name="Check_warning_15_minute")
def main():

    all_warnings = getWarning()
    warnings = checkWarning(all_warnings)
    msg = generate_message(warnings)
    send_message(msg)
    trigger_trigger(warnings)
    send_emails(msg)


if __name__ == "__main__":
    main()
