import chromadb
import asyncio
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from celery import shared_task
from django.db.models import Q
import logging
from asgiref.sync import sync_to_async
"""Periodic task(INSERTS data in vector db) celery beat/per rooom(future scope) """

def dbOp():
    from base.models import VectorDbAdditionStatus
    vecdbstat=VectorDbAdditionStatus.objects.filter(Q(status=False))
    for v in vecdbstat:
        v.status=True
        v.save()
    return vecdbstat


# @shared_task
# def populate():
#     try:
#         chroma_client =chromadb.HttpClient(host='localhost',port=3000)
#         collection=chroma_client.get_or_create_collection("all_rooms_data")
        
#         vecdbstat=dbOp()
#         if len(vecdbstat)<1 :return 
#         ids=[]
#         name=[]
#         descriptions=[]
#         tags=[]
#         parent_topics=[]
#         topics=[]

#         for v in vecdbstat:
#             room=v.room
#             ids.append(room.id)
#             name.append(room.name)
#             descriptions.append(room.description)
#             tags.append(room.tags["tags"])
#             parent_topics.append(room.parent_topic.topic)
#             topics.append(room.topic)

#         collection.add(
#             ids=[str(id) for id in ids],
            
#             documents=[
#                 f"""
#                 name:{name[idx]}
#                 description:{descriptions[idx]}
#                 tags:{tags[idx]}
#                 topic:{topics[idx]}
#                 parent_topic:{parent_topics[idx]}
#                 """ for idx,_ in enumerate(name)]
#             ,
#             metadatas=[{"room name":name,"room id":id} for id,name in zip(ids,name)]
#         )

#         num_embeddings=collection.count()
#         print(f"Total embedding in vecDb:{num_embeddings}")
#     except Exception as e:
#         logging.fatal(f"❌❌ERROR in creating/getting chroma collection :{str(e)}")


@shared_task
def populate():
    from base.models import VectorDbAdditionStatus
    try:
        # ✅ Always create the client once per process
        chroma_client = chromadb.HttpClient(host="localhost", port=3000)

        # ✅ Get or create the target collection
        collection = chroma_client.get_or_create_collection("all_rooms_data")

        # ✅ Fetch records to be embedded
        vecdbstat = dbOp()
        if not vecdbstat:
            logging.info("No new rooms to add to Chroma.")
            logging.info(f"✅ Successfully populated Chroma. Total embeddings: {collection.count()}")

            return

        # ✅ Prepare lists (avoid reusing variable names)
        ids = []
        documents = []
        metadatas = []

        for v in vecdbstat:
            room = v.room

            # Defensive checks
            if not room:
                continue

            ids.append(str(room.id))

            # ✅ Construct document text cleanly (no extra indentation)
            doc_text = (
                f"name: {room.name}\n"
                f"description: {room.description}\n"
                f"tags: {', '.join(room.tags.get('tags', [])) if isinstance(room.tags, dict) else room.tags}\n"
                f"topic: {room.topic}\n"
                f"parent_topic: {room.parent_topic.topic if hasattr(room.parent_topic, 'topic') else room.parent_topic}"
            )
            documents.append(doc_text)

            metadatas.append({
                "room_name": room.name,
                "room_id": room.id
            })

        # ✅ Add all embeddings in one batch
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        # ✅ Confirm insertion
        num_embeddings = collection.count()
        logging.info(f"✅ Successfully populated Chroma. Total embeddings: {num_embeddings}")

    except Exception as e:
        logging.fatal(f"❌ ERROR while populating Chroma: {str(e)}")

