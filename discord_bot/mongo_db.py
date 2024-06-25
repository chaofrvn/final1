from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import asyncio
import pandas as pd
import uuid

from dotenv import load_dotenv
import os

load_dotenv("../.env")
uri = os.environ["MONGODB_URL"]
client = AsyncIOMotorClient(uri, server_api=ServerApi("1"))
database = client["finalProject"]
warningCollection = database["warning"]
EmailCollection = database["email"]


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
    time_type: bool,
    period: int | None,
    compare: bool,
    thresold: float,
):

    warning = {
        "_id": uuid.uuid4().hex[:24],
        "ticker": ticker,
        "field": field,
        "indicator": indicator,
        "period": period,
        "thresold": thresold,
        "is_greater": compare,
        "is_15_minute": time_type,
        "trigger": True,
    }
    existing_document = await warningCollection.find_one({"user_id": user_id})

    if existing_document:
        # If the document exists, push the new warning to the warnings array
        result = await warningCollection.update_one(
            {"user_id": user_id}, {"$push": {"warnings": warning}}
        )
    else:
        # If the document does not exist, create it with the new warning
        result = await warningCollection.insert_one(
            {"user_id": user_id, "warnings": [warning], "email": None}
        )
    return result
    # result = await warningCollection.insert_one(warning)

    # return "result %s" % repr(result.inserted_id)


async def getWarning(user_id):
    # warnings = await warningCollection.find({"user_id": user_id}).to_list(None)
    # return warnings
    warnings = await warningCollection.aggregate(
        [
            {"$match": {"user_id": user_id}},  # Match the specific document
            {
                "$project": {"warnings": 1, "_id": 0}
            },  # Project only the items array, exclude _id
        ]
    ).to_list(None)
    # if warnings is None:
    #     return None
    # else:
    #     return warnings[0]["warnings"]
    return warnings


async def getWarningByObjectID(user_id, id):
    # warning = await warningCollection.find_one(
    #     {"user_id": user_id, "_id": ObjectId(id)}
    # )
    # return warning
    warning = await warningCollection.find_one(
        {"user_id": user_id, "warnings._id": id},
        {"warnings.$": 1, "_id": 0},  # Project only the matched item in the array
    )
    if warning is None:
        return None
    else:
        return warning["warnings"][0]


async def deleteWarning(id):

    result = await warningCollection.update_one(
        {"warnings._id": id}, {"$pull": {"warnings": {"_id": id}}}
    )

    return result


async def updateWarning(id, new_warning):
    # await warningCollection.find_one_and_replace({"_id": ObjectId(id)}, new_warning)

    result = await warningCollection.update_one(
        {"warnings._id": id},
        {"$set": {"warnings.$[elem]": new_warning}},
        array_filters=[{"elem._id": id}],
    )
    return result


async def setEmail(id, email):
    result = await warningCollection.update_one(
        {"user_id": id},
        {"$set": {"email": email}, "$setOnInsert": {"user_id": id, "warnings": []}},
        upsert=True,  # Create the document if it doesn't exist
    )
    return f"Email đã được cập nhật."


async def getEmail(id):
    result = await warningCollection.find_one({"user_id": id})
    if result is not None and result["email"] is not None:
        return "Email của bạn là " + result["email"]

    else:
        return "Bạn chưa có email hãy thêm email để nhận cảnh báo"


async def deleteEmail(id):
    result = await warningCollection.find_one({"user_id": id})

    if result != None and result["email"] != None:
        await warningCollection.update_one({"user_id": id}, {"$set": {"email": None}})
        return "Bạn đã xóa email thành công"
    else:
        return "Bạn chưa có email"


async def main():
    # result = await addWarning(
    #     user_id=1122766688497172520,
    #     ticker="BID",
    #     time_type=True,
    #     field="close",
    #     thresold=40,
    #     compare=True,
    #     indicator=None,
    #     period=None,
    # )
    #
    # result = await getWarningByObjectID(
    #     user_id=112276668849717520, id="67ddfb53ed0d4724a54ee55f"
    # )
    # result = await getWarning(user_id=112276668849717250)

    # result = await getEmail(1122766688497172520)
    result = await deleteWarning("b06d41b5825d43a9a0742813")
    # result = await deleteEmail(1122766688497172520)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
