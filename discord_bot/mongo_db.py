from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio
import pandas as pd

# phai dung motor chu khong phai pymongo
from dotenv import load_dotenv
import os

load_dotenv("../.env")
uri = os.environ["MONGODB_URL"]
client = AsyncIOMotorClient(uri, server_api=ServerApi("1"))
database = client["finalProject"]
warningCollection = database["warning"]


# Create a new client and connect to the server
async def ping_server():

    # Send a ping to confirm a successful connection
    try:
        await client.admin.command("ping")
        value = await client.list_database_names()
        print(value)
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


async def addWarning(
    user_id: int,
    ticker: str,
    field: str,
    indicator: str,
    time_type: str,
    period: int | None,
    compare: str,
    thresold: float,
):

    warning = {
        "user_id": user_id,
        "ticker": ticker,
        "field": field,
        "indicator": indicator,
        "period": period,
        "thresold": thresold,
        "is_greater": compare,
        "is_15_minute": time_type,
        "trigger": True,
    }
    result = await warningCollection.insert_one(warning)
    return "result %s" % repr(result.inserted_id)


async def getWarningsDataFrame(user_id):
    warnings = await warningCollection.find({"user_id": user_id}).to_list(None)

    # Chuyển đổi danh sách cảnh báo thành DataFrame
    if warnings:
        df = pd.DataFrame(warnings)
        df.index += 1  # Đánh số index bắt đầu từ 1
        df["alert_id"] = df.index  # Thêm cột alert_id
        return df
    else:
        return pd.DataFrame()


def formatWarningsMarkdown(df):
    if df.empty:
        return "You have no warnings."
    else:
        # Lựa chọn các cột cần thiết và đổi tên các cột cho dễ hiểu
        df = df[
            [
                "alert_id",
                "ticker",
                "field",
                "indicator",
                "thresold",
                "period",
                "is_greater",
                "is_15_minute",
            ]
        ]
        df.columns = [
            "Alert ID",
            "Ticker",
            "Field",
            "Indicator",
            "Threshold",
            "Period",
            "Is_greater",
            "Is_15m",
        ]
        return df.to_markdown(index=True)


async def getWarning(user_id):
    user_id = user_id  # Thay bằng user_id của bạn
    df = await getWarningsDataFrame(user_id)
    markdown = f"```\n{formatWarningsMarkdown(df=df)}\n```"
    return markdown


if __name__ == "__main__":
    asyncio.run(getWarning())
