# import influxdb_client_3
# from influxdb_client_3.client.write_api import SYNCHRONOUS
from influxdb_client_3 import Point,InfluxDBClient3,WritePrecision
INFLUXDB_TOKEN="PmPx_j2QNxnawqadS0TikSExG3ufx90JV8oRMLw0rftX1NLy6gLi5ntL3Q-QahCiJ_MgcTX6XAsUNVbRwVjR5w=="
import time
org = "Thai"
host = "https://us-central1-1.gcp.cloud2.influxdata.com"
client = InfluxDBClient3(host=host, token=INFLUXDB_TOKEN, org=org)
database="stock_data"

def push_data(stock):
    point=Point("stock_prize").tag("ticker",stock['ticker']).field("open",stock['open']).field("close",stock['close']).field("low",stock['low']).field("high",stock['high']).field("volume",stock['volume']).time(int(stock['time']),write_precision=WritePrecision.S)
    client.write(database=database, record=point)

