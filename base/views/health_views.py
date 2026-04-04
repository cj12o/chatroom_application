from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from ..services import chroma_services


@api_view(["GET"])
@permission_classes([AllowAny])
def chroma_health(request):
    try:
        info = chroma_services.health_check()
        return Response(
            {
                "status": "healthy",
                "host": settings.CHROMA_HOST,
                "port": settings.CHROMA_PORT,
                **info,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {
                "status": "unhealthy",
                "host": settings.CHROMA_HOST,
                "port": settings.CHROMA_PORT,
                "error": str(e),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
