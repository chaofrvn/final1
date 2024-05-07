# import influxdb_client_3
# from influxdb_client_3.client.write_api import SYNCHRONOUS
from influxdb_client_3 import Point,InfluxDBClient3,WritePrecision
import os
from dotenv import load_dotenv
import time
load_dotenv("../.env")
INFLUXDB_TOKEN=os.environ["INFLUXDB_TOKEN"]

org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient3(host=host, token=INFLUXDB_TOKEN, org=org)
database="stock_data"

def push_data(stock):
    point=Point("stock_prize").tag("ticker",stock['ticker']).field("open",stock['open']).field("close",stock['close']).field("low",stock['low']).field("high",stock['high']).field("volume",stock['volume']).time(int(stock['time']),write_precision=WritePrecision.S)
    client.write(database=database, record=point)

