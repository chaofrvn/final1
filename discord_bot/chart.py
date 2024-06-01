import matplotlib.pyplot as plt
import numpy as np
import io
import matplotlib as mpl
import matplotlib.dates as mdates
from matplotlib.pyplot import figure

dayFmt = mdates.DateFormatter("%Y-%m-%d", tz="Asia/Ho_Chi_Minh")
hourFmt = mdates.DateFormatter("%H:%M")
import asyncio
from influx_db import get_all_time_data


async def all_time_chart(ticker, field, data, title=""):
    data_stream = io.BytesIO()
    figure(figsize=(8, 6), dpi=80)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(dayFmt)
    for column in data.columns:
        plt.plot(data.index, data[column], label=column)
    plt.xticks(rotation=60)
    plt.title(f"All time {field} value of")
    plt.gcf().subplots_adjust(bottom=0.2)
    plt.savefig(data_stream, format="png", bbox_inches="tight", dpi=80)
    plt.close(fig)
    data_stream.seek(0)
    return data_stream


async def one_day_chart(ticker, field, data, title=""):
    data_stream = io.BytesIO()
    figure(figsize=(8, 6), dpi=80)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(hourFmt)
    # print('------------------2-----------------------')
    for column in data.columns:
        plt.plot(data.index, data[column], label=column)
    plt.xticks(rotation=60)
    plt.title(f"One day {field} value of")
    plt.gcf().subplots_adjust(bottom=0.2)
    plt.savefig(data_stream, format="png", bbox_inches="tight", dpi=80)
    plt.close(fig)
    data_stream.seek(0)
    return data_stream


async def main():
    data = await get_all_time_data(ticker="BID", indicator="rsi", period="14")
    data_stream = await asyncio.gather(all_time_chart("VCB", "close", data=data))
    with open("output_image.png", "wb") as output_file:
        output_file.write(data_stream[0].read())


if __name__ == "__main__":
    asyncio.run(main())
