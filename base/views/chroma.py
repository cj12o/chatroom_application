import chromadb
import asyncio
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models.room_model import Room
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

collection=None

@api_view(['POST'])
def topk(request):
    try:
        query=request.data["query"]
        print(f"Query:{query}")
        results =collection.query(
            query_texts=[query], # Chroma will embed this for you
            n_results=3 # how many results to return
        )
        print(results["documents"][0])
        if results:
            return Response({
                "id":[int(id) for id in results["ids"][0]],
                "rooms":[room for room in results["documents"][0]]
            },status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error":str(e)
        },status=status.HTTP_400_BAD_REQUEST)


def populate():
    try:
        rooms=Room.objects.all().values('name','description','id')
        for room in rooms:
            name=room["name"]
            description=room["description"]
            id=room["id"]
            print(f"room id:{id} name={name} description :{description}")
            collection.add(
                ids=[str(id)],
                documents=[
                    f"Room name:{name} description:{description}"
                ]
            )
    except Exception as e:
        print(f"Error:{str(e)}")


try:
    collection=chroma_client.get_collection("rooms")
    chroma_client.delete_collection("rooms")
    populate()
except Exception:
    collection=chroma_client.create_collection("rooms")
    populate()
