from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from base.models import Room, Message
from base.tasks.agent_task import main as agent_main, savePolltoDb, saveThreadToDb, connectToWs
from base.services.rate_limiter import check_and_increment
from base.logger import logger
from asgiref.sync import async_to_sync


class BoostRoomView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, pk):
        try:
            room = Room.objects.get(id=pk)

            if not check_and_increment(request.user.id, "agent"):
                return Response(
                    {"error": "Rate limit exceeded. Try again later."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            last_messages = (
                Message.objects.filter(room_id=pk, is_unsafe=False)
                .order_by("-created_at")[:10]
            )

            chat_summary = "\n".join(
                f"{msg.author.username}: {msg.message}"
                for msg in reversed(last_messages)
            ) if last_messages else ""

            agent_result = agent_main(
                room_id=room.id,
                room_name=room.name,
                room_description=room.description,
                chat_summary=chat_summary,
            )

            if agent_result and "tool_called" in agent_result:
                if agent_result["tool_called"] == "pollGenerator":
                    savePolltoDb(
                        room_id=room.id,
                        username="Agent",
                        message=agent_result["content"],
                    )
                else:
                    message_id = saveThreadToDb(
                        room_id=room.id,
                        username="Agent",
                        message=agent_result["content"],
                    )
                    async_to_sync(connectToWs)(
                        tool_called="threadGenerator",
                        message=agent_result["content"],
                        message_id=message_id,
                        room_id=room.id,
                    )

                return Response(
                    {"message": "Room boosted", "tool_called": agent_result["tool_called"]},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": "Agent did not produce a result."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Boost room error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
