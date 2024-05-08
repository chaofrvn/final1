# import influxdb_client_3
# from influxdb_client_3.client.write_api import SYNCHRONOUS
from influxdb_client import Point,InfluxDBClient,WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv
import time
load_dotenv("../.env")
INFLUXDB_TOKEN=os.environ["INFLUXDB_TOKEN"]

org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient(url=host, token=INFLUXDB_TOKEN, org=org)
bucket="stock_data"
write_api = client.write_api(write_options=SYNCHRONOUS)
def push_data(stock):
    point=Point(stock["type"]).tag("ticker",stock['ticker']).field("open",stock['open']).field("close",stock['close']).field("low",stock['low']).field("high",stock['high']).field("volume",stock['volume']).time(int(stock['time']),write_precision=WritePrecision.S)
    write_api.write(bucket=bucket, record=point)

