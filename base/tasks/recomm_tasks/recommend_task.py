from celery import shared_task
from django.db.models import Q
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import chromadb
"GET user recomm "
import chromadb
import logging


# @shared_task
def HistList(username:str,x:int,k:int)->dict:
    from base.models import History
    from django.contrib.auth.models import User
    try:
        """
        method that returns list of user visited room
        mech: from top k sessions-->get top x rooms ordered by time spent-->return a list

        hist:{
        "room_id":20000,
        "room2":3990,
        "room3":670,
        ...
        }
        """
        dct_to_send={}

        hists=History.objects.filter(Q(user__username=username)).order_by("-created_at")
        session_counter=k
        for h in hists:
            if session_counter==0:break
            json_hst=h.hist
            # print(f"Type:{type(json_hst)}")
            if len([k for k  in json_hst.keys()])<1:continue
            #     continue #remove sesh where no rooms were visited

            # if type(json_hst)!="dict":raise ValueError("incorrect type of data in history ,not dict format")
            sorted_json=sorted(json_hst.items(),key=lambda tupl_:tupl_[1],reverse=True) #sorted based  on max timespent
            sorted_json_dct={k:v for k,v in sorted_json}

            counter=0
            dct_temp={}
            for k,v in sorted_json_dct.items():
                if counter==x:break
                dct_temp[k]=v
                counter+=1
            
            # print(f"------DCT {dct_temp}")
            
            dct_to_send[h.session]=dct_temp
            session_counter=session_counter-1
        
        # print(f"DCT TO send {dct_to_send}")
        return dct_to_send
    except  Exception as e:
        logging.fatal(str(e))


# @shared_task
def getCosinSimRooms(user_history_dict:dict)->list:
    from base.models import Room
    try:

        chroma_client =chromadb.HttpClient(host='localhost',port=3000)
        collection=chroma_client.get_or_create_collection("all_rooms_data")
        
        res_lst=[]
        for k,v in user_history_dict.items():
            for r_id,_ in v.items():
                print(f"COSINE SIM :{r_id}")
                room=Room.objects.get(id=r_id)
                
                query_doc=f"""
                    name:{room.name}
                    description:{room.description}
                    tags:{room.tags["tags"]}
                    topic:{room.topic}
                    parent_topic:{room.parent_topic.topic}
                """ 
                
                results =collection.query(
                    query_texts=[query_doc], 
                    n_results= 6 if collection.count()>6 else collection.count()
                )
                # for result in results:
                metadata=results["metadatas"][0]
                documents=results["documents"][0]
                for i in range(0,len(metadata)):
                    # print(f"✏️room name:{metadata[i]["room name"]} id:{metadata[i]["room id"]} document:{documents[i]}")
                    dct={"id":int(metadata[i]["room_id"]),"name":metadata[i]["room_name"],"document":documents[i]}
                    res_lst.append(dct)
        
        return res_lst
    except Exception as e:
        print(f"ERROR in getCosinSimRooms:{str(e)}")






