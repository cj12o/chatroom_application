from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from ..models.join_request_model import JoinRequest, RequestStatus
from ..models.room_model import Room
from ..models.notification_model import Notification
from ..serializers.join_request_serializer import JoinRequestSerializer
from ..tasks.notification_task import createNotification
from ..logger import logger

class RequestJoinView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            room_id = request.data.get('room_id')
            if not room_id:
                return Response({"error": "Room ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            room = get_object_or_404(Room, id=room_id)

            if not room.is_private:
                return Response({"error": "This room is public"}, status=status.HTTP_400_BAD_REQUEST)

            if room.members.filter(id=request.user.id).exists():
                return Response({"error": "You are already a member"}, status=status.HTTP_400_BAD_REQUEST)

            join_request, created = JoinRequest.objects.get_or_create(user=request.user, room=room)

            if not created:
                if join_request.status == RequestStatus.PENDING:
                    return Response({"error": "Request already pending"}, status=status.HTTP_400_BAD_REQUEST)
                if join_request.status == RequestStatus.ACCEPTED:
                    return Response({"error": "You are already a member"}, status=status.HTTP_400_BAD_REQUEST)
                
                # If REJECTED, reset to PENDING
                join_request.status = RequestStatus.PENDING
                join_request.save()
            
            # Notify Room Admin (Author)
            # We need to create a notification for the admin. 
            # Since Notification model requires a Message, we might need a system message or adjust the model.
            # For now, let's assume we can create a system message or use a different notification mechanism if available.
            # But based on existing notification_task, it seems tightly coupled with Message.
            # Let's try to create a dummy message or see if we can bypass it.
            # Actually, the user requirement says "manage request create a section in notification page".
            # This implies we might need a different way to fetch these requests, or integrate them into notifications.
            # Let's create a notification for the admin.
            
            # For now, we will just return success. The admin will fetch requests via ListJoinRequestsView.
            # But to notify, we might need to send a WS message directly or create a Notification object.
            # Let's stick to the plan: "Implement notifications for requests and status updates".
            # We'll handle notification logic in a separate step or improved task if needed.
            
            return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in RequestJoinView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListJoinRequestsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            # List requests for rooms where the current user is the author (admin)
            rooms = Room.objects.filter(author=request.user)
            requests = JoinRequest.objects.filter(room__in=rooms, status=RequestStatus.PENDING)
            serializer = JoinRequestSerializer(requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in ListJoinRequestsView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ManageJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            request_id = request.data.get('request_id')
            action = request.data.get('action') # 'ACCEPT' or 'REJECT'

            if not request_id or not action:
                return Response({"error": "Request ID and action are required"}, status=status.HTTP_400_BAD_REQUEST)

            join_request = get_object_or_404(JoinRequest, id=request_id)

            # Verify that the current user is the admin of the room
            if join_request.room.author != request.user:
                return Response({"error": "You are not authorized to manage this request"}, status=status.HTTP_403_FORBIDDEN)

            if action == 'ACCEPT':
                join_request.status = RequestStatus.ACCEPTED
                join_request.save()
                join_request.room.members.add(join_request.user)
                # Notify user
                
            elif action == 'REJECT':
                join_request.status = RequestStatus.REJECTED
                join_request.save()
                # Notify user
                
            else:
                return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": f"Request {action.lower()}ed"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in ManageJoinRequestView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
