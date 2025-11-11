from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status   
from django.contrib.auth.models import User
from django.db.models import Q
from ..tasks.recomm_tasks.llm_task import orchestrator
from ..tasks.recomm_tasks.chroma_task import populate
from ..models import History
import json
class TestView(APIView):
    # def get(self, request):
    #     try:
    #         dct={}
    #         username="neymar"
    #         room_name="Messi The messia"
    #         user=User.objects.get(username=username)
            
    #         member=user.room_member.filter(Q(name=room_name))
        
    #         if len(member)>0:
    #             dct["member"]=True
    #         else: dct["member"]=False
            
    #         room=user.author_rooms.filter(Q(name=room_name))
    #         if len(room)>0:
    #             dct["room"]=True
    #         else : dct["room"]=False
            
    #         mod=user.room_moderator.filter(Q(name=room_name))
    #         if len(mod)>0:
    #             dct["mod"]=True
    #         else : dct["mod"]=False
        
    #         return Response({
    #             "data":dct
    #         }, status=status.HTTP_200_OK)
        
    #     except Exception as e:
    #         return Response({
    #             "error":str(e)
    #         },status=status.HTTP_400_BAD_REQUEST)
    def get(self,request):    
        try:
        #     """
        #     method that returns list of user visited room
        #     mech: from top k sessions-->get top x rooms ordered by time spent-->return a list

        #     hist:{
        #     "room_id":20000,
        #     "room2":3990,
        #     "room3":670,
        #     ...
        #     }
        #     """
        #     dct_to_send={}
        #     k=2
        #     x=2
        #     hists=History.objects.filter(Q(user__username="alex")).order_by("-created_at")[:k]
        #     for h in hists:

        #         json_hst=h.hist
        #         print(f"Type:{type(json_hst)}")
        #         # if len([k for k  in json_hst.keys])<1:
        #         #     continue #remove sesh where no rooms were visited

        #         # if type(json_hst)!="dict":raise ValueError("incorrect type of data in history ,not dict format")
        #         sorted_json=sorted(json_hst.items(),key=lambda tupl_:tupl_[1],reverse=True) #sorted based  on max timespent
        #         sorted_json_dct={k:v for k,v in sorted_json}

        #         counter=0
        #         dct_temp={}
        #         for k,v in sorted_json_dct.items():
        #             if counter==x:break
        #             dct_temp[k]=v
        #             counter+=1
                
        #         print(f"------DCT {dct_temp}")
                
        #         dct_to_send[h.session]=dct_temp
            orchestrator.delay("alex",2,2)
            # populate.delay()
            return Response({
                "msg":"ok"
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)

