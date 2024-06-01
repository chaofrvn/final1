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


async def getWarning(user_id):

    warnings = await warningCollection.find({"user_id": user_id}).to_list(None)
    return warnings


if __name__ == "__main__":
    asyncio.run(getWarning())
