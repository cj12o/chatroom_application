import chromadb
from celery import shared_task
from django.db.models import Q
import logging
from django.conf import settings
"""Periodic task(INSERTS data in vector db) celery beat scheduler"""

def dbOp():
    "returns rooms that are not populated in vector db and makes their populates status True"
    try:
        from base.models import VectorDbAdditionStatus
        from base.logger import logger
        vecdbstat=VectorDbAdditionStatus.objects.filter(Q(status=False))
        for v in vecdbstat:
            v.status=True
            v.save()
        return vecdbstat
    except Exception as e:
        logger.error(e)
        


@shared_task
def populate():
    """
    populates vector Db:
    1)if any new rooms(vecdbstat)
    2)populate 
    3)log the status
    """
    try:
        from base.logger import logger
        
        chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )

        collection = chroma_client.get_or_create_collection("all_rooms_data")

        # Fetch records to be embedded
        vecdbstat = dbOp()
        if not vecdbstat:
            logging.info("No new rooms to add to Chroma.")
            logging.info(f"✅ Successfully populated Chroma. Total embeddings: {collection.count()}")

            return

        
        ids = []
        documents = []
        metadatas = []

        for v in vecdbstat:
            room = v.room

            # Defensive checks
            if not room:
                continue

            ids.append(str(room.id))

        
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

        # Adding  all embeddings in one batch
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        # validate insertion
        num_embeddings = collection.count()
        logger.info(f"✅ Successfully populated Chroma. Total embeddings: {num_embeddings}")

    except Exception as e:
        logger.error(f"❌ ERROR while populating Chroma: {str(e)}")

