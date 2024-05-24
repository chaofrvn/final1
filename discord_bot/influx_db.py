from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime,time
import asyncio
import functools
import pandas as pd
import typing
from datetime import datetime
import pandas_ta as ta
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
def get_all_time_data(ticker:str,field="close",indicator='normal',period=12):
    query=f'''from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r.ticker == "{ticker}" and r._measurement=="stock_daily")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''


    df:pd.DataFrame=query_api.query_data_frame(query=query)
    df.set_index('_time', inplace=True)

    
    match indicator:
        case 'normal':
            df=df[field].dropna().to_frame()
        case 'ma':
            df['MA'] = ta.sma(df[field], length=period)
            # Create a new DataFrame with only the time and the indicator
            df = df[['MA']].dropna()

        case 'ema':
            df['EMA'] = ta.ema(df[field], length=period)
            # Create a new DataFrame with only the time and the indicator
            df = df[['EMA']].dropna()
            # Rename columns if necessary
            # df.rename(columns={'index': '_time', 'EMA': 'Indicator'}, inplace=True)
        case 'stoch':
            df[['STOCH_k', 'STOCH_d']] = ta.stoch(df['high'], df['low'], df['close'])
            # Create a new DataFrame with only the time and the indicator
            df = df[['STOCH_k', 'STOCH_d']].dropna()

        case 'rsi':
            df['RSI'] = ta.rsi(df['close'], length=14)
            df=df[['RSI']].dropna()
    return df
@to_thread
def get_single_day_data(ticker:str,day=datetime.now().date().strftime('%d-%m-%Y')):
    date_object = datetime.strptime(day, '%d-%m-%Y')
    start_timestamp = int(datetime.combine(date_object, time.min).timestamp())
    end_timestamp = int(datetime.combine(date_object, time.max).timestamp())
    query=f'''from(bucket: "stock_data")
    |> range(start:{start_timestamp},stop:{end_timestamp})
    |> filter(fn: (r) => r._measurement == "stock_price")
    |> filter(fn: (r) => r.ticker == "{ticker}")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df=query_api.query_data_frame(query=query)
    
    return df

async def main():
    res= await asyncio.gather(get_single_day_data(ticker="HPG"))
    return res
if __name__=="__main__":  
   print(asyncio.run(main()))