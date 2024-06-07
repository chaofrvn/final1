import discord
from discord.ext import commands
from confluent_kafka import Consumer, KafkaException
import threading
import asyncio
import socket


class ReceiveWarning(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.consumer = None
        self.consumer_task = None
        self.loop = asyncio.get_event_loop()
        self.running = False

    @commands.Cog.listener()
    async def on_ready(self):
        print("Receive warning cog loaded")

    def start_consumer(self):
        config = {
            "bootstrap.servers": "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": "HGLHHLIGH5YQYKVX",
            "sasl.password": "gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9",
            "group.id": "stock_price_group",
            "auto.offset.reset": "earliest",  # Start from the latest message
            "client.id": socket.gethostname(),
        }
        self.consumer = Consumer(config)
        self.consumer.subscribe(["stockWarning"])
        self.running = True
        self.consumer_task = self.loop.create_task(self.consume_messages())

    async def consume_messages(self):
        while self.running:
            msg = await self.loop.run_in_executor(None, self.consumer.poll, 1.0)
            print(msg)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    print(f"Reached end of partition: {msg.partition()}")
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    continue
            await self.process_message(msg.value().decode("utf-8"), int(msg.key()))

    async def process_message(self, message, user_id):
        print(f"Received message: {message}")
        # Add your asynchronous processing logic here
        user = await self.bot.fetch_user(user_id)
        await user.send(message)

    def stop_consumer(self):
        self.running = False
        if self.consumer_task:
            self.consumer_task.cancel()
        if self.consumer:
            self.consumer.close()

    def cog_unload(self):
        self.stop_consumer()
        print(f"{self.__class__.__name__} unloaded and Kafka consumer closed.")


async def setup(bot):
    ...
    # cog = ReceiveWarning(bot)
    # cog.start_consumer()
    # await bot.add_cog(cog)
    # print("KafkaCog setup complete.")
