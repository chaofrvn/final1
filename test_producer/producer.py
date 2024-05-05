from confluent_kafka import Producer
import socket
from itertools import repeat
import time as t
from vnstock import * #import all functions
import multiprocessing as mp
import pandas as pd
from prefect import flow, task
import math
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import numpy as np

import schedule
conf = {'bootstrap.servers': 'pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'HGLHHLIGH5YQYKVX',
        'sasl.password': 'gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9',
        'client.id': socket.gethostname()}
a = True
producer = Producer(conf)
kafka_topic="stockPrice"
today = str((datetime.now()-timedelta(days=1)).date())
# today = '2024-04-09'
# cur_time = datetime.now()

stock_symbols = pd.read_csv("company.csv")['ticker'].tolist()
# stock_symbols.remove("ROS")
# stock_symbols.remove("TKC")
print(len(stock_symbols))

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    # else:
    #     print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def send_to_kafka(producer, topic, key, message):
    # Sending a message to Kafka
    # producer.produce(topic, key=key, partition=0, value=json.dumps(message).encode("utf-8"))
    # print(producer, topic, key, message)
    producer.produce(topic, key=key, value=json.dumps(message).encode("utf-8"), callback=delivery_report)
    producer.flush()


def retrieve_real_time_data(stock_symbols):

    # print(f"process starts")
    df=pd.DataFrame()
    # if not stock_symbols:
    #     print(f"No stock symbols provided in the environment variable.")
    #     exit(1)
    # print(stock_symbols)
    while True:
        # Fetch real-time data for the last 1 minute
 
        is_market_open_bool = True
        if is_market_open_bool:
            for symbol_index, stock_symbol in enumerate(stock_symbols):
                try:
                    # print(stock_symbol)
                    real_time_data = stock_historical_data(symbol=stock_symbol, start_date= today , end_date= today , resolution="15", type="stock", beautify=False, decor=False, source='DNSE')
                    if real_time_data is not None and not real_time_data.empty:
                        # stock_time = datetime.strptime(real_time_data.iloc[-1,0], "%Y-%m-%d %H:%M:%S")
                        # if True:
                        #     real_time_data.iloc[-1,0]=stock_time.timestamp()
                        #     # print(stock_time.timestamp())
                        #     latest_data_point = real_time_data.iloc[-1].to_dict()
                        #     send_to_kafka(producer, kafka_topic, stock_symbol, latest_data_point)
                        df=df._append(real_time_data.iloc[-1])
                        # df=pd.concat([df,real_time_data.iloc[-1]],axis=0)
                except Exception as e:
                    print(f"Error processing stock symbol {stock_symbol}: {str(e)}")
                    continue
        else:
            print("Market is closing")
        # t.sleep(5)
        return df
        break
def divide_list(input_list, num_sublists):
    sublist_length = math.ceil(len(input_list) / num_sublists)
    return [input_list[i:i+sublist_length] for i in range(0, len(input_list), sublist_length)]
@task
def collect_data():
    num_of_thread=100
    with ThreadPoolExecutor() as pool:
        return list(pool.map(retrieve_real_time_data,divide_list(stock_symbols,num_of_thread)))
@task
def transform_data(data):
    df=pd.concat(data)
    if df.empty:
        return df
    df.loc[:,'time']=pd.to_datetime(df.loc[:,'time']).dt.tz_localize('Asia/Ho_Chi_Minh').values.astype(np.int64) // 10 ** 9
    return df
@task
def load_data(df):
    for index, row in df.iterrows():
        row=row.to_dict()
        send_to_kafka(producer=producer,topic=kafka_topic,key=row['ticker'],message=row)
# @task
# def finel(): 
#     schedule.every(15).minutes.do(collect_data)
#     collect_data()
  
@flow
def main():
    data=collect_data()
    transformed_data=transform_data(data)
    load_data(transformed_data)

if __name__ == '__main__':
    main()


