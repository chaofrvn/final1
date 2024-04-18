from confluent_kafka import Producer
import socket
from itertools import repeat
import time as t
from vnstock import * #import all functions
import multiprocessing as mp
import pandas as pd
conf = {'bootstrap.servers': 'pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'MPT6ORJOO7EOIBBT',
        'sasl.password': '/NjGhfqfDTWlLmh2d5iUeKdqz6Bm9POPBEH8S9fv0BiRsIXGmn68CYqPI1lfiOUA',
        'client.id': socket.gethostname()}
a = True
producer = Producer(conf)
stock_symbols = pd.read_csv("company.csv")['ticker'].tolist()
stock_symbols.remove("ROS")
stock_symbols.remove("TKC")
print(len(stock_symbols))
def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def send_to_kafka(producer, topic, key, message):
    # Sending a message to Kafka
    # producer.produce(topic, key=key, partition=0, value=json.dumps(message).encode("utf-8"))
    # print(producer, topic, key, message)
    producer.produce(topic, key=key, value=json.dumps(message).encode("utf-8"), callback=delivery_report)
    producer.flush()

def retrieve_real_time_data(producer, kafka_topic,stock_symbols):
    producer=Producer(conf)
    print(f"process starts")
    # stock_symbols = stock_symbol.split(",") if stock_symbol else []
    # print(stock_symbols)
    # a = True
    # time_str = "2024-04-02 14:45:00"
    # b = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    if not stock_symbols:
        print(f"No stock symbols provided in the environment variable.")
        exit(1)
    # print(stock_symbols)
    while True:
        # Fetch real-time data for the last 1 minute
        is_market_open_bool = True
        if is_market_open_bool:
            # print("huhu")
            for symbol_index, stock_symbol in enumerate(stock_symbols):
                # print(1)
                # real_time_data = stock_historical_data(symbol=stock_symbol, start_date="2024-04-16", end_date="2024-04-16", resolution="15", type="stock", beautify=False, decor=False, source='DNSE')
                # print(symbol_index,stock_symbol)
                # if not real_time_data.empty:
                #     # Convert and send the latest real-time data point to Kafka
                #     latest_data_point = real_time_data.iloc[-1].to_dict()
                #     # print(latest_data_point)
                #     send_to_kafka(producer, kafka_topic, stock_symbol, latest_data_point)
                try:
                    real_time_data = stock_historical_data(symbol=stock_symbol, start_date="2024-04-16", end_date="2024-04-16", resolution="15", type="stock", beautify=False, decor=False, source='DNSE')
                    if not real_time_data.empty:
                        latest_data_point = real_time_data.iloc[-1].to_dict()
                    send_to_kafka(producer, kafka_topic, stock_symbol, latest_data_point)
                except Exception as e:
                    print(f"Error processing stock symbol {stock_symbol}: {str(e)}")
                    continue
        else:
            print("Market is closing")
        # t.sleep(5)
        break
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
if __name__ == '__main__':
    # retrieve_real_time_data(producer, 'topic_0',stock_symbols)
    num_of_process=2
    process=[]
    for i in range(num_of_process):
        process.append(mp.Process(name=f'process {i}',target=retrieve_real_time_data,args=(producer,'topic_0',list(chunks(stock_symbols,int(1608/num_of_process)))[i])))
        # process.append(mp.Process(name=f'process {i}',target=retrieve_real_time_data,args=(producer, 'topic_0',)))
        process[i].start()
    # with mp.Pool() as pool:
    #     results: list[str] = pool.starmap(retrieve_real_time_data, zip(repeat(producer),repeat('topic_0'),list(chunks(stock_symbols,402))))
    #     print(f"Results: {results}")
    # print(f"Core available: {mp.cpu_count()}")



