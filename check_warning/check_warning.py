from confluent_kafka import Producer
import socket
import pandas as pd
from prefect import flow, task,get_run_logger
import logging
from dotenv import load_dotenv
import os
from confluent_kafka import Producer
import socket
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio
import operator
from influxdb_client import InfluxDBClient
from get_value import get_value
logging.basicConfig(filename="logging.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w')
 
# Creating an object
logger = logging.getLogger()
load_dotenv("../.env")
conf = {'bootstrap.servers': "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': "HGLHHLIGH5YQYKVX",
        'sasl.password': 'gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9',
        'client.id': socket.gethostname()}
producer = Producer(conf)
kafka_topic="stockWarning"
uri = os.environ["MONGODB_URL"]
INFLUXDB_TOKEN=os.environ["INFLUXDB_TOKEN"]
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
database=client["finalProject"]
warningCollection=database["warning"]
org = os.environ["INFLUXDB_ORG"]
host = os.environ["INFLUXDB_HOST"]
client = InfluxDBClient(url=host, token=INFLUXDB_TOKEN, org=org)
database="stock_data"
query_api=client.query_api()
@task
async def getWarning():
    warnings=await warningCollection.find().to_list(None)
    return warnings
@task
def checkWarning(warnings):
    comparison_funcs = {
        (True, True): operator.ge,  # trigger is True and is_greater is True (>=)
        (True, False): operator.le, # trigger is True and is_greater is False (<=)
        (False, True): operator.gt, # trigger is False and is_greater is True (>)
        (False, False): operator.lt # trigger is False and is_greater is False (<)
    } 
    datas={}
    df=pd.DataFrame()

    for warning in warnings:
        data=None
        if warning["ticker"] in datas:
            data=datas[warning["ticker"]]
        else:
            query=f'''from(bucket: "stock_data")
        |> range(start:0)
        |> filter(fn: (r) => r.ticker == "{warning["ticker"]}" and r._measurement=="{"stock_price" if warning["is_15_minute"]else "stock_daily"}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
            data=query_api.query_data_frame(query=query,data_frame_index=["_time"])
            datas[warning["ticker"]]=data
            # print(data.index)

        value:pd.DataFrame=get_value(df=data,indicator=warning["indicator"],field=warning["field"],period=warning["period"])
        # if(comparison_funcs[(warning["is_greater"],warning["trigger"])]):
        row = pd.DataFrame({'value': [value["value"][0]],'trigger':warning["trigger"],'ticker':warning["ticker"],'user_id':warning["user_id"],'thresold':warning["thresold"],'field':warning["field"],"indicator":warning["indicator"]}, index=[value.index[0]])
        df=pd.concat([df,row])
    df.index.name="_time"
    print("\n"+df.to_markdown(tablefmt="grid"))
@flow
async def main():
    warnings=await getWarning()
    checkWarning(warnings)
if __name__=="__main__":
    asyncio.run(main())