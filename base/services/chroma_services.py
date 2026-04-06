import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from django.conf import settings

from base.logger import logger

COLLECTION_NAME = "all_rooms_data"

_embedding_fn = None

def get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-3-small",
        )
    return _embedding_fn


def get_client():
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )


def get_collection(name=COLLECTION_NAME):
    return get_client().get_or_create_collection(name, embedding_function=get_embedding_fn())


def add_room(room):
    """Add a single room embedding to ChromaDB."""
    try:
        collection = get_collection()
        doc_text = (
            f"name: {room.name}\n"
            f"description: {room.description}\n"
            # f"tags: {', '.join(room.tags.get('tags', [])) if isinstance(room.tags, dict) else room.tags}\n"
            # f"topic: {room.topic}\n"
            # f"parent_topic: {room.parent_topic.topic if hasattr(room.parent_topic, 'topic') else room.parent_topic}"
        )
        collection.add(
            ids=[str(room.id)],
            documents=[doc_text],
            metadatas=[{"room_name": room.name, "room_id": room.id}],
        )
        logger.info(f"Added room {room.id} to ChromaDB")
    except Exception as e:
        logger.error(f"Failed to add room {room.id} to ChromaDB: {e}")


def update_room(room):
    """Update OR Create a room embedding in ChromaDB."""
    try:
        collection = get_collection()
        doc_text = (
            f"name: {room.name}\n"
            f"description: {room.description}\n"
        )
        
        # Use upsert instead of update
        collection.upsert(
            ids=[str(room.id)],
            documents=[doc_text],
            metadatas=[{"room_name": room.name, "room_id": room.id}],
        )
        logger.info(f"Upserted room {room.id} in ChromaDB")
    except Exception as e:
        logger.error(f"Failed to upsert room {room.id} in ChromaDB: {e}")

def delete_room(room_id):
    """Delete a room embedding from ChromaDB."""
    try:
        collection = get_collection()
        collection.delete(ids=[str(room_id)])
        logger.info(f"Deleted room {room_id} from ChromaDB")
    except Exception as e:
        logger.error(f"Failed to delete room {room_id} from ChromaDB: {e}")


def query_rooms(query_text, n_results=3):
    """Query ChromaDB for similar rooms."""
    collection = get_collection()
    return collection.query(query_texts=[query_text], n_results=n_results)


def health_check():
    """Return ChromaDB health info or raise on failure."""
    client = get_client()
    heartbeat = client.heartbeat()
    collections = client.list_collections()
    return {
        "heartbeat": heartbeat,
        "collections_count": len(collections),
    }
