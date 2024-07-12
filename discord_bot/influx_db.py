from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime, time
import asyncio
import functools
import pandas as pd
import typing
import inspect
import sys


load_dotenv("../.env")
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from util.caculate_indicator import (
    get_all_data_point,
    get_latest_data_point,
    caculate_analaytic_data,
)

INFLUXDB_TOKEN = os.environ["INFLUXDB_TOKEN"]
vietnam_timezone = pytz.timezone("Asia/Ho_Chi_Minh")
org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient(url=host, token=INFLUXDB_TOKEN, org=org)
database = "stock_data"
query_api = client.query_api()


def to_thread(func: typing.Callable) -> typing.Coroutine:
    """Run a blocking function inside a thread for non blocking

    Args:
        func (typing.Callable): The blocking function

    Returns:
        typing.Coroutine: The Thread
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)

    return wrapper


@to_thread
def get_latest_data(
    ticker: str, field: str = None, indicator: str = None, period: int = None
) -> pd.DataFrame:
    query = f"""from(bucket:"stock_data")
|> range(start: 0)
|> filter(fn:(r) => r._measurement == "stock_price")
|> filter(fn:(r) => r.ticker == "{ticker}")
|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
|> sort(columns:["_time"], desc: true)
|> limit(n:100)
"""

    # df=write_api.write(query=query)
    # print(df)
    df = query_api.query_data_frame(query=query)
    df.set_index("_time", inplace=True)
    # print(df)
    df = df.iloc[::-1]
    # print(df)
    df = get_latest_data_point(df, field=field, indicator=indicator, period=period)
    df.index = df.index.tz_convert("Asia/Ho_Chi_minh").strftime("%Y-%m-%d %H:%M:%S")
    return df.iloc[0]


@to_thread
def get_latest_daily_data(
    ticker: str, field: str = None, indicator: str = None, period: int = None
):
    query = f"""from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r._measurement == "stock_daily")
    |> filter(fn: (r) => r.ticker == "{ticker}")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    |> sort(columns:["_time"], desc: true)
    |> limit(n:100)
    """
    df = query_api.query_data_frame(query=query)
    # print(df)
    df = df.iloc[::-1]
    # print(df)
    df.set_index("_time", inplace=True)
    df = get_latest_data_point(df, field=field, indicator=indicator, period=period)

    df.index = df.index.tz_convert("Asia/Ho_Chi_minh").strftime("%Y-%m-%d")
    return df.iloc[0]


@to_thread
def get_all_time_data(ticker: str, field=None, indicator=None, period=12):
    query = f"""from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r.ticker == "{ticker}" and r._measurement=="stock_daily")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    """

    df: pd.DataFrame = query_api.query_data_frame(query=query)
    df.set_index("_time", inplace=True)
    df = get_all_data_point(df, field=field, indicator=indicator, period=period)
    return df


@to_thread
def get_single_day_data(
    ticker: str,
    field=None,
    indicator=None,
    day=datetime.now().date().strftime("%d-%m-%Y"),
    period=12,
):
    date_object = datetime.strptime(day, "%d-%m-%Y")
    timezone = pytz.timezone("Asia/Ho_Chi_Minh")
    start = datetime.combine(date_object, time.min, tzinfo=timezone)
    end = datetime.combine(date_object, time.max, tzinfo=timezone)
    query = f"""from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r._measurement == "stock_price")
    |> filter(fn: (r) => r.ticker == "{ticker}")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    """
    df: pd.DataFrame = query_api.query_data_frame(query=query)
    df.set_index("_time", inplace=True)

    df = get_all_data_point(df=df, field=field, indicator=indicator, period=period)
    df = df.loc[start:end]
    return df


@to_thread
def get_analaytic_data(ticker: str):
    query = f"""from(bucket: "stock_data")
    |> range(start:0)
    |> filter(fn: (r) => r.ticker == "{ticker}" and r._measurement=="stock_daily")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    """
    df: pd.DataFrame = query_api.query_data_frame(query=query)
    df.set_index("_time", inplace=True)
    df = caculate_analaytic_data(df)
    print(df)
    return df


async def main():
    res = await asyncio.gather(get_latest_data(ticker="VCB", field="close"))
    return res


if __name__ == "__main__":
    print(asyncio.run(main()))
