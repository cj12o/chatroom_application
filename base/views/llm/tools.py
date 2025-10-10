from ...models import History
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_userHistory(request):
    print(f"request:{request.user.id}")
    history=History.objects.filter(Q(user__id=request.user.id)).order_by("-created_at")[0:3]
    for hist in history:
        print(f"{hist.rooms_visited} created_at{hist.created_at}")

    return Response({
        "message":"ok"
    },status=status.HTTP_200_OK)






