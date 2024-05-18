from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio
# phai dung motor chu khong phai pymongo
from dotenv import load_dotenv
import os

load_dotenv("../.env")
uri = os.environ["MONGODB_URL"]
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
database=client["finalProject"]
warningCollection=database["warning"]
# Create a new client and connect to the server
async def ping_server():
    
    # Send a ping to confirm a successful connection
    try:
        await client.admin.command('ping')
        value=await client.list_database_names()
        print(value)
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
      
async def addWarning(user_id:int,ticker:str,indicator:str,time_type:str,period:int,compare:str,thresold:float):
    is_15_minute=False if time_type=="1D" else True
    is_greater=True if compare=="GREATER" else False
    warning={
        "user_id":user_id,
        "ticker":ticker,
        "indicator":indicator,
        "period":period,
        "thresold":thresold,
        "is_greater":is_greater,
        "is_15_minute":is_15_minute,
        "trigger":True
    }
    result = await warningCollection.insert_one(warning)
    return "result %s" % repr(result.inserted_id)
if __name__=="__main__":
    asyncio.run(addWarning())