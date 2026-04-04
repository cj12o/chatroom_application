import chromadb
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


@api_view(["GET"])
@permission_classes([AllowAny])
def chroma_health(request):
    try:
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
        heartbeat = client.heartbeat()
        collections = client.list_collections()
        return Response(
            {
                "status": "healthy",
                "host": settings.CHROMA_HOST,
                "port": settings.CHROMA_PORT,
                "heartbeat": heartbeat,
                "collections_count": len(collections),
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
