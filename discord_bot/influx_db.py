from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime
load_dotenv("../.env")
INFLUXDB_TOKEN=os.environ["INFLUXDB_TOKEN"]
vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient(url=host, token=INFLUXDB_TOKEN, org=org)
database="stock_data"
query_api=client.query_api()
def get_latest_price(ticker:str):
    query = f'''from(bucket:"stock_data")
|> range(start: 0)
|> filter(fn:(r) => r._measurement == "stock_price")
|> filter(fn:(r) => r.ticker == "{ticker}")
|> filter(fn:(r) => r._field=="close")
|> last()
'''
    table=query_api.query(query=query)
    # df=write_api.write(query=query)
    # print(df)
    value=table.to_values(['_value','_time'])
    value[0][1]=value[0][1].astimezone(vietnam_timezone)
    return value[0]
def get_latest_daily_volume(ticker:str):
    query=f'''from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r._measurement == "stock_daily")
    |> filter(fn: (r) => r._field == "volume")
    |> filter(fn: (r) => r.ticker == "{ticker}")
    |> last()'''

if __name__=="__main__":
    print(get_latest_price("HPG")[1])