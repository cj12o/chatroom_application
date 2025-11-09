import chromadb
import asyncio
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from celery import shared_task
from django.db.models import Q
# from ...models import Room
# from ...models import Topic
# from .helper import gettopksesh
# from .llm import Recommend

collection=None


#TODO: optimize timestampwise fetch and check vector are not redundant
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

@shared_task
def getCollection():
    global collection
    try:
        collection=chroma_client.get_or_create_collection("all_rooms_data")
    except Exception:
        print(f"ERROR in creating chroma collection")


@shared_task
def populate():
    from base.models import VectorDbAdditionStatus
   
    try:
        global collection
        vecdbstat=VectorDbAdditionStatus.objects.filter(Q(status=False))

        ids=[]
        name=[]
        descriptions=[]
        tags=[]
        parent_topics=[]
        topics=[]

        for v in vecdbstat:
            room=v.room
            ids.append(room.id)
            name.append(room.name)
            descriptions.append(room.description)
            tags.append(room.tags["tags"])
            parent_topics.append(room.parent_topic.topic)
            topics.append(room.topic)

        collection.add(
            ids=[str(id) for id in ids],
            
            documents=[
                f"""
                name:{name[idx]}
                description:{descriptions[idx]}
                tags:{tags[idx]}
                topic:{topics[idx]}
                parent_topic:{parent_topics[idx]}
                """ for idx,_ in enumerate(name)]
            ,
            metadatas=[{"room name":name,"room id":id} for id,name in zip(ids,name)]
        )
    except:
        print(f"❌❌ERROR in adding vector db")

