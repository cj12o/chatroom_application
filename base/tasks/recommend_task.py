from celery import shared_task
from django.contrib.auth.models import User
from django.db.models import Q
import chromadb
"GET user recomm "



chroma_client = chromadb.HttpClient(host='localhost', port=8000)
collection=chroma_client.get_collection("all_rooms_data")

@shared_task
def recomList(username:str,x:int,k:int)->dict:
    from base.models import History
    try:
        """
        method that returns list of recommendation
        mech: from top k sessions-->get top x rooms ordered by time spent-->return a list

        hist:{
        "room_id":20000,
        "room2":3990,
        "room3":670,
        ...
        }
        """
        dct_to_send={}

        hists=History.objects.filter(Q(user__username=username)).order_by("- created_at")[:k]
        for h in hists:
            json_hst=h.hist["history"]
            if len(json_hst.keys())<1:continue #remove sesh where no rooms were visited

            if type(json_hst)!="dict":raise ValueError("incorrect type of data in history ,not dict format")
            sorted_json=dict(sorted(json_hst.items(),key=lambda tupl_:tupl_[1],reverse=True)) #sorted based  on max timespent
            
            counter=0
            dct_temp={}
            for k,v in sorted_json.items():
                if counter==x:return
                dct_temp[k]=v
                counter+=1
            
            dct_temp[h.session]=dct_temp


    except  Exception as e:
        pass


@shared_task
def getCosinSimRooms(user_history_dict:dict)->list:
    from base.models import Room
    try:
        global collection

        res_lst=[]
        for r_id,_ in user_history_dict:
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
                n_results=2 
            )
            # for result in results:
            metadata=results["metadatas"][0]
            documents=results["documents"][0]
            for i in range(0,len(metadata)):
                # print(f"✏️room name:{metadata[i]["room name"]} id:{metadata[i]["room id"]} document:{documents[i]}")
                dct={"id":metadata[i]["room id"],"name":metadata[i]["room name"],"document":documents[i]}
                res_lst.append(dct)
        
        return res_lst
    except Exception as e:
        print(f"ERROR in getCosinSimRooms:{str(e)}")


