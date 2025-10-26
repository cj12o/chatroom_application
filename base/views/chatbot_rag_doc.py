# from ..models.message_model import Vote,Message
# from django.db.models import Q
# from langchain_community.document_loaders import DirectoryLoader
# import asyncio 

# def createDoc(id:int=None):
#     #todo id+full
#     messages=Message.objects.filter(Q(room__id=id))
#     with open("text_rag_files/Rag_data.txt","w") as file:
#         for m in messages:
#             dct={}
#             dct["chat"]=m.message
#             dct["chat_author"]=m.author.username
#             votes=Vote.objects.filter(Q(message_id=m.id))
#             dct["upvotes"]=len(votes.filter(Q(vote=1)))
#             dct["downvotes"]=len(votes.filter(Q(vote=-1)))

#             for k,v in dct.items():
#                 file.write(f"{k}:{v}\n")
            
#     Rag()

            
# def Rag():
#     try:
#         loader=DirectoryLoader("text_rag_files")
#         documents = loader.lazy_load()
#         print(f"🐐🐐Doc loader=>")
#         for document in documents:
#             print(document)
#     except Exception as e:
#         print(f"❌❌Error in Rag:{e}")

    