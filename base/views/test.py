from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status   
from django.contrib.auth.models import User
from django.db.models import Q

class TestView(APIView):
    def get(self, request):
        try:
            dct={}
            username="neymar"
            room_name="Messi The messia"
            user=User.objects.get(username=username)
            
            member=user.room_member.filter(Q(name=room_name))
        
            if len(member)>0:
                dct["member"]=True
            else: dct["member"]=False
            
            room=user.author_rooms.filter(Q(name=room_name))
            if len(room)>0:
                dct["room"]=True
            else : dct["room"]=False
            
            mod=user.room_moderator.filter(Q(name=room_name))
            if len(mod)>0:
                dct["mod"]=True
            else : dct["mod"]=False
        
            return Response({
                "data":dct
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)