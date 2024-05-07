from influxdb_client_3 import InfluxDBClient3
import os
from dotenv import load_dotenv
import time
load_dotenv("../.env")
INFLUXDB_TOKEN=os.environ["INFLUXDB_TOKEN"]

org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient3(host=host, token=INFLUXDB_TOKEN, org=org)
database="stock_data"

def get_latest_price(ticker:str):
    query=f'SHOW COLUMNS FROM stock_prize'
    client.query(query="""SELECT * FROM 'stock_prize'""",database="stock_data")
    # df=write_api.write(query=query)
    # print(df)
get_latest_price("BID")