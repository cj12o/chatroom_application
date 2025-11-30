from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q,Case,Count,When,BooleanField
from ...models import Room,Message   
from ...serializers.message_serializer import MessageSerializerForModeration
from ...logger import logger
from ...serializers.room_serializer import RoomSerializerForModeration
from ...models.Room_Moderation_model import ModerationType
from ...tasks import add_summerize_task
class ModerationMessageApiview(APIView):

    permission_classes=[IsAuthenticated]
    authentication_classes=[TokenAuthentication]

    def get(self,request,pk):
        "return list of messages in a room"
        try:
            rooms=Room.objects.filter(Q(moderator__id=request.user.id)&Q(id=pk))
            room=rooms[0]

            "case :Semi mod ->return only flaged"
            if room.room_moderation_type.moderation_type==ModerationType.SemiAuto:
                msgs=room.room_message.filter(Q(is_semi_moderated=True)&Q(is_flaged_as_unsafe=True))
                serializer=MessageSerializerForModeration(msgs,many=True)
            
                return Response(serializer.data,status=status.HTTP_200_OK)
            
            "case :manual mod ->return all msgs"
            msgs=room.room_message.filter(Q(is_moderated=False))
            serializer=MessageSerializerForModeration(msgs,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(e)
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    def post(self,request,pk):
        "mark message as moderated"
        try:
            room=Room.objects.filter(Q(moderator__id=request.user.id)&Q(id=pk))
            if len(room)<1:
                return Response({"status":"You are not a moderator of this room"},status=status.HTTP_400_BAD_REQUEST)
            
            id_no_action_needed=request.data.get("no_action_needed",[])
            id_action_needed=request.data.get("action_needed",[])
        
            total_ids=id_no_action_needed+id_action_needed
            if len(total_ids)<1:
                return Response({"status":"No messages to moderate"},status=status.HTTP_200_OK)

            if len(id_action_needed)>0:
                Message.objects.filter(id__in=id_action_needed).update(is_unsafe=True,message="removed By Moderators,as it was voilating safety guidelines")
                ##trigger summerization
            if len(id_no_action_needed)>=10:
                add_summerize_task.delay({"room_id":pk})
            Message.objects.filter(id__in=total_ids).update(is_moderated=True)

        
            return Response({"status":"successfully moderated msgs"},status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({"status":f"Error:{str(e)}"},status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])       
def getRoomsForModeration(request):
    "return list of rooms in which  a user is assigned as moderator and has unmoded messages"
    try:
        rooms_ids=[r.id for r in request.user.room_moderator.all()]
        qs=Room.objects.annotate(
            count_unmoded_messages=Count('room_message',filter=Q(room_message__is_moderated=False)&Q(id__in=rooms_ids)),
            has_message_to_mod=Case(
                When(count_unmoded_messages__gt=0,then=True),
                default=False,
                output_field=BooleanField()
            )
        )
        qs=qs.filter(has_message_to_mod=True)
        serializer=RoomSerializerForModeration(qs,many=True)
       
        return Response(serializer.data,status=status.HTTP_200_OK)        
    except Exception as e:
        logger.error(e)
        return Response({"status":"bad","error":str(e)},status=status.HTTP_400_BAD_REQUEST)
 

