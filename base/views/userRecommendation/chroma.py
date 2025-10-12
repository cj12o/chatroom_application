# import chromadb
# import asyncio
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status

# from ...models import Room
# from ...models import Topic
# from .helper import gettopksesh
# from .llm import Recommend


# #TODO: optimize timestampwise fetch and check vector are not redundant
# chroma_client = chromadb.HttpClient(host='localhost', port=8000)

# try:
#     if chroma_client.get_collection("all_rooms_data"):
#         chroma_client.delete_collection("all_rooms_data")
# except Exception:
#     pass 
# finally:
#     collection=chroma_client.create_collection("all_rooms_data")

# room_lst=[]



# def cosSimList(room_lst:list)->list:
#     recom_lst=[]
    
#     for room in room_lst:
#         results =collection.query(
#             query_texts=[room], 
#             n_results=3 
#         )
#         print(recom_lst.append(results["documents"][0]))
    
        
#     print(f"Recomendation:{recom_lst}")
#     return recom_lst


# @api_view(['POST'])
# def topk(request):
#     try:
#         query=request.data["query"]
#         print(f"Query:{query}")
#         results =collection.query(
#             query_texts=[query], # Chroma will embed this for you
#             n_results=3 # how many results to return
#         )
#         print(results["documents"][0])
#         if results:
#             return Response({
#                 "id":[int(id) for id in results["ids"][0]],
#                 "rooms":[room for room in results["documents"][0]]
#             },status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({
#             "error ":str(e)
#         },status=status.HTTP_400_BAD_REQUEST)

# # seperate for parent_topics
# def create_collections():
#     try:
#         if chroma_client.get_collection("all_rooms_data"):
#             chroma_client.delete_collection("all_rooms_data")
#     except Exception:
#         pass 
#     finally:
#         collection=chroma_client.create_collection("all_rooms_data")
#     # topics=Topic.objects.all()
#     # try:
#     #     for topic in topics:
#     #         # print(f"topic:{topic.topic}")
#     #         coll=chroma_client.get_or_create_collection(topic.topic)
#     #         collection_mapper[topic.topic]=coll
#     #     # print(collection_mapper.keys())
#     # except Exception as e:
#     #     print(f"Error in create_collections {str(e)}")
        


# def populate():
#     # try:
#     rooms=Room.objects.all().values('name','description','id','parent_topic__topic')
#     for room in rooms:
#         name=room["name"]
#         description=room["description"]
#         parent_topic=room["parent_topic__topic"]
#         id=room["id"]
#         # print(f"room id:{id} name={name} description :{description}")
#         # collection_mapper[parent_topic].add(
#         #     ids=[str(id)],
#         #     documents=[
#         #         f"Room name:{name} description:{description} "
#         #     ]
#         # )

#         collection.add(
#             ids=[str(id)],
#             documents=[
#                 f"Room name:{name} description:{description} "
#             ]
#         )
#     print("✅✅Embeddings created")
#     room_lst=gettopksesh()
#     recom_lst=cosSimList(room_lst=room_lst)
#     Recommend(room_list=recom_lst,user_history=room_lst)


# populate()