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
import logging
logging.basicConfig(filename="logging.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w')
 
# Creating an object
logger = logging.getLogger()
conf = {'bootstrap.servers': 'pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'HGLHHLIGH5YQYKVX',
        'sasl.password': 'gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9',
        'client.id': socket.gethostname()}
a = True
producer = Producer(conf)
kafka_topic="stockPrice"
now=datetime.now()
today = str(now.date())

# today = '2024-05-03'

stock_symbols = pd.read_csv("company.csv")['ticker'].tolist()


def delivery_report(err, msg):
    if err is not None:
        logger.error('Message delivery failed: {}'.format(err))
    else:
        logger.info('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def send_to_kafka(producer, topic, key, message):
    # Sending a message to Kafka
    producer.produce(topic, key=key, value=json.dumps(message).encode("utf-8"), callback=delivery_report)
    producer.flush()


def retrieve_real_time_data(stock_symbols):
    df=pd.DataFrame()



    for symbol_index, stock_symbol in enumerate(stock_symbols):
        try:
            real_time_data = stock_historical_data(symbol=stock_symbol, start_date= today , end_date= today , resolution="15", type="stock", beautify=False, decor=False, source='DNSE')
            if real_time_data is not None and not real_time_data.empty:
                df=df._append(real_time_data.iloc[-1])
        except Exception as e:
            logger.error(f"Error processing stock symbol {stock_symbol}: {str(e)}")
            continue

    return df

def divide_list(input_list, num_sublists):
    sublist_length = math.ceil(len(input_list) / num_sublists)
    return [input_list[i:i+sublist_length] for i in range(0, len(input_list), sublist_length)]
@task
def collect_data():
    num_of_thread=50
    with ThreadPoolExecutor() as pool:
        return list(pool.map(retrieve_real_time_data,divide_list(stock_symbols,num_of_thread)))
@task
def transform_data(data):
    df=pd.concat(data)
    if df.empty:
        logger.info('There is no data')
        return df
    df.loc[:,'time']=pd.to_datetime(df.loc[:,'time']).dt.tz_localize('Asia/Ho_Chi_Minh').values.astype(np.int64) // 10 ** 9
    ts_25min_ago = int((now-timedelta(minutes=25)).timestamp())
    df=df.loc[df['time']>ts_25min_ago]
    logger.info('Transform data successfully')
    return df
@task
def load_data(df):
    for index, row in df.iterrows():
        row=row.to_dict()
        send_to_kafka(producer=producer,topic=kafka_topic,key=row['ticker'],message=row)
        logger.info('Send data to kafka successfully')

  
@flow
def main():
    data=collect_data()
    transformed_data=transform_data(data)
    load_data(transformed_data)

if __name__ == '__main__':
    main()


