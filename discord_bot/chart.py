import matplotlib.pyplot as plt
import numpy as np
import io
import matplotlib as mpl
import matplotlib.dates as mdates
from matplotlib.pyplot import figure

dayFmt = mdates.DateFormatter("%Y-%m-%d", tz="Asia/Ho_Chi_Minh")
hourFmt = mdates.DateFormatter("%H:%M", tz="Asia/Ho_Chi_Minh")
import asyncio
from influx_db import get_all_time_data, get_single_day_data


def generate_title(ticker, field, indicator: str, type):
    title = "Biểu đồ nội nhật của " if type == "one_day" else "Biểu đồ hàng ngày của "
    if indicator is None:
        title += f"trường {field} "
    elif field is None:
        title += f"chỉ báo {indicator.upper()} "
    else:
        title += f"chỉ báo {indicator.upper()} của trường {field} "
    title += f"của mã cổ phiếu {ticker}"
    return title


def all_time_chart(ticker, field, indicator, data):
    data_stream = io.BytesIO()

    figure(figsize=(8, 6), dpi=80)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(dayFmt)
    for column in data.columns:
        plt.plot(data.index, data[column], label=column)
    plt.xlabel("Thời gian")
    plt.ylabel("Giá trị")
    plt.legend()
    plt.xticks(rotation=60)
    plt.title(
        generate_title(ticker=ticker, field=field, indicator=indicator, type="all_time")
    )
    plt.gcf().subplots_adjust(bottom=0.2)
    plt.savefig(data_stream, format="png", bbox_inches="tight", dpi=80)
    plt.close(fig)
    data_stream.seek(0)
    return data_stream


def one_day_chart(ticker, field, indicator, data):
    data_stream = io.BytesIO()
    figure(figsize=(8, 6), dpi=80)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(hourFmt)
    for column in data.columns:
        plt.plot(data.index, data[column], label=column)

    plt.xlabel("Thời gian")
    plt.ylabel("Giá trị")
    plt.legend()
    plt.xticks(rotation=60)
    plt.title(
        generate_title(ticker=ticker, field=field, indicator=indicator, type="one_day")
    )

    plt.gcf().subplots_adjust(bottom=0.2)
    plt.savefig(data_stream, format="png", bbox_inches="tight", dpi=80)
    plt.close(fig)
    data_stream.seek(0)
    return data_stream


async def main():
    data = await get_all_time_data(ticker="BID", indicator="macd")
    data_stream = all_time_chart("BID", field=None, indicator="macd", data=data)
    with open("output_image.png", "wb") as output_file:
        output_file.write(data_stream.read())


if __name__ == "__main__":
    asyncio.run(main())
