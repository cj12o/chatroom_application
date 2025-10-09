from ..chroma import chroma_client
import asyncio

history_collection = None

async def create_collection(username:str):
    history_collection = await chroma_client.create_collection(f"{username}_history")


