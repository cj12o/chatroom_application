from ..models.room_model import Room
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view
from ..logger import logger
from django.db.models import Count,When,Case,Value

    
@api_view(['POST'])
def giveSuggestions(request):
    """
    give suggestions to search bar on homepage
    takes formdata
    """
    try:
        suggestions=[]
        keyword=request.data['keyword'].strip().lower()
        if len(keyword)<1:raise Exception("Empty keyword")
        
    
        rooms=Room.objects.annotate(
            message_count=Count("room_message"),
            matched_field=Case(
                When(name__icontains=keyword,then=Value("name")),
                When(topic__icontains=keyword,then=Value("topic")),
                When(parent_topic__topic__icontains=keyword,then=Value("parent_topic")),
                When(author__username__icontains=keyword,then=Value("author")),
                When(tags__icontains=keyword,then=Value("tags"))
            )
        ).filter(
            Q(name__icontains=keyword)|
            Q(topic__icontains=keyword)|
            Q(parent_topic__topic__icontains=keyword)|
            Q(author__username__icontains=keyword)|
            Q(tags__icontains=keyword)).order_by("-updated_at","-message_count","-created_at")[:6]
            
        
        for room in rooms:
        
            matched={}
            field_matched=room.matched_field

            if field_matched=="tags":
                for t in room.tags['tags']:
                    if keyword in t.lower():
                        matched["tag"]=t

            elif field_matched=="parent_topic":
                matched[field_matched]=room.parent_topic.topic
            
            elif field_matched=="author":
                matched[field_matched]=room.author.username

            else:matched[field_matched]=room.__getattribute__(field_matched)
       
            suggestions.append((room.name,room.id,matched))
            
        return Response({"suggestions":suggestions},status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response({"suggestions":"Unable to fetch suggstions at momment"},status=status.HTTP_400_BAD_REQUEST)





