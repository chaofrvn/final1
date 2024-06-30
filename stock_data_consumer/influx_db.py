# import influxdb_client_3
# from influxdb_client_3.client.write_api import SYNCHRONOUS
import threading
from influxdb_client import Point, InfluxDBClient, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS, WriteOptions
import os
from dotenv import load_dotenv
import time
import logging
from queue import Queue

logging.basicConfig(
    filename="logging.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="a",
    force=True,
)
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger()
logger.info("startin.....")
load_dotenv("../.env")
INFLUXDB_TOKEN = os.environ["INFLUXDB_TOKEN"]

org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient(url=host, token=INFLUXDB_TOKEN, org=org, timeout=50000)
bucket = "stock_data"
write_api = client.write_api(
    write_options=WriteOptions(batch_size=1000, flush_interval=10_000)
)

message_queue = Queue()


def push_data():
    while True:
        stock = message_queue.get()
        if stock is None:
            break
        try:
            point = (
                Point(stock["type"])
                .tag("ticker", stock["ticker"])
                .field("open", stock["open"])
                .field("close", stock["close"])
                .field("low", stock["low"])
                .field("high", stock["high"])
                .field("volume", stock["volume"])
                .time(int(stock["time"]), write_precision=WritePrecision.S)
            )
            write_api.write(bucket=bucket, record=point)
            logger.info(f"Successfully push data for {stock['ticker']}")
        except Exception as err:
            logger.error(f"Error processing stock symbol {stock['ticker']}: {str(err)}")
        finally:
            message_queue.task_done()


def start_worker_threads(num_threads=10):
    worker_threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=push_data)
        t.daemon = True
        t.start()
        worker_threads.append(t)
    return worker_threads


def shutdown_workers(worker_threads):
    for _ in worker_threads:
        message_queue.put(None)
    for t in worker_threads:
        t.join()


def close_influxdb_client():
    client.close()
