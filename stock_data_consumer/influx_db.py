# import influxdb_client_3
# from influxdb_client_3.client.write_api import SYNCHRONOUS
from influxdb_client import Point, InfluxDBClient, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
import os
from dotenv import load_dotenv
import time
import logging

logging.basicConfig(
    filename="logging.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
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
write_api = client.write_api(write_options=SYNCHRONOUS)


def push_data(stock):
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
