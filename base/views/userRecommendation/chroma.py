from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ...services import chroma_services
from .helper import gettopksesh
from .llm import Recommend


def cosSimList(room_lst: list) -> list:
    res_lst = []
    for room in room_lst:
        results = chroma_services.query_rooms(room["description"], n_results=2)
        metadata = results["metadatas"][0]
        documents = results["documents"][0]
        for i in range(len(metadata)):
            dct = {
                "id": metadata[i]["room id"],
                "name": metadata[i]["room name"],
                "description": documents[i],
            }
            res_lst.append(dct)
    return res_lst


@api_view(["POST"])
def topk(request):
    try:
        query = request.data["query"]
        print(f"Query:{query}")
        results = chroma_services.query_rooms(query, n_results=3)
        print(results["documents"][0])
        if results:
            return Response(
                {
                    "id": [int(id) for id in results["ids"][0]],
                    "rooms": [room for room in results["documents"][0]],
                },
                status=status.HTTP_200_OK,
            )
    except Exception as e:
        return Response({"error ": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def getRecommendation(username: str):
    room_lst = gettopksesh(username=username)
    recom_lst = cosSimList(room_lst=room_lst)
    result_lst = Recommend(room_list=recom_lst, user_history=room_lst)
    return result_lst
