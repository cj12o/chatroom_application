from celery import shared_task
# @shared_task
# async def createDoc():
#     wrapper.delay(1)
import os
from base.models.message_model import Vote,Message
from django.db.models import Q
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveJsonSplitter
from langchain_ollama import OllamaEmbeddings

from django.conf import settings
# def wrapper(id:int=None):
def createDoc(id:int=None):
    #laxy loading
    
    


    #todo id+full
    messages=Message.objects.filter(Q(room__id=id))
    with open("text_rag_files/Rag_data.txt","w") as file:
        # doc={}
        # idx=1
        for m in messages:
            dct={}
            dct["chat"]=m.message
            dct["chat_author"]=m.author.username
            votes=Vote.objects.filter(Q(message_id=m.id))
            dct["upvotes"]=len(votes.filter(Q(vote=1)))
            dct["downvotes"]=len(votes.filter(Q(vote=-1)))
            print(f"😀😀TASK dct->{dct}")
            
            # doc[idx]=dct
            # idx=idx+1
            for k,v in dct.items():
                file.writelines(f"{k}:{v}\n")
            file.write("\n")
                
            
    # Rag(doc)
    Rag()

            
# def Rag(documents:dict):
def Rag():
    try:

        base=settings.BASE_DIR
        loader=DirectoryLoader(os.path.join(base,"text_rag_files"))
        documents=loader.load()
        for d in documents:
            print()
        print("Doc loaded")               
        # embedding_model=OllamaEmbeddings(model="nomic-embed-text:v1.5")
        # splitter=RecursiveJsonSplitter(max_chunk_size=200)
        # chunks=splitter.split_text(documents)
        # for chnk in chunks:
        #     print(f"Chunks:{chnk}")
        
        

    except Exception as e:
        print(f"❌❌Error in Rag:{e}")

    