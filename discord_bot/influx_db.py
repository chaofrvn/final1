from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime
import asyncio
import functools
import pandas as pd
import typing
from datetime import datetime,_Date
load_dotenv("../.env")
INFLUXDB_TOKEN=os.environ["INFLUXDB_TOKEN"]
vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient(url=host, token=INFLUXDB_TOKEN, org=org)
database="stock_data"
query_api=client.query_api()
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)
    return wrapper
@to_thread
def get_latest_data(ticker:str)->pd.DataFrame:
    query = f'''from(bucket:"stock_data")
|> range(start: 0)
|> filter(fn:(r) => r._measurement == "stock_price")
|> filter(fn:(r) => r.ticker == "{ticker}")
|> last()
|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

    # df=write_api.write(query=query)
    # print(df)
    df=query_api.query_data_frame(query=query)
    df["_time"]=df["_time"].dt.tz_convert("Asia/Ho_Chi_minh").dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.iloc[0]
@to_thread
def get_latest_daily_data(ticker:str):
    query=f'''from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r._measurement == "stock_daily")
    |> filter(fn: (r) => r.ticker == "{ticker}")
    |> last()
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df=query_api.query_data_frame(query=query)
    df["_time"]=df["_time"].dt.tz_convert("Asia/Ho_Chi_minh").dt.strftime('%Y-%m-%d')
    return df.iloc[0]
    # return value[0]


@to_thread
def get_all_time_data(ticker:str):
    query=f'''from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r._measurement == "stock_daily")
    |> filter(fn: (r) => r.ticker == "{ticker}")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df=query_api.query_data_frame(query=query)
    # df["_time"]=df["_time"].dt.tz_convert("Asia/Ho_Chi_minh").dt.strftime('%Y-%m-%d')
    return df
@to_thread
def get_single_day_data(ticker:str,day:_Date=datetime.now().date()):
    start_timestamp = datetime.combine(day, datetime.time(0, 0, 0)).timestamp()
    end_timestamp = datetime.combine(day, datetime.time(23, 59, 59)).timestamp()
    query=f'''from(bucket: "stock_data")
    |> range(start:{start_timestamp},stop:{end_timestamp})
    |> filter(fn: (r) => r._measurement == "stock_price")
    |> filter(fn: (r) => r.ticker == "{ticker}")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df=query_api.query_data_frame(query=query)
    return df
@to_thread
def get_moving_average(ticker,period,field,time_type):
    query=f'''
from(bucket: "stock_data")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "{"stock_daily"if time_type=="1D"else "stock_price"}" and r._field == "{field}" and r.ticker =="{ticker}")
  |> movingAverage(n: {period}) // Adjust the window size (n) as needed
  |> keep(columns: ["_time", "_value"])
'''
    df=query_api.query_data_frame(query=query)
    return df
async def main():
    res= await asyncio.gather(get_latest_daily_data("HPG"))
    return res
if __name__=="__main__":  
   print(asyncio.run(main()))