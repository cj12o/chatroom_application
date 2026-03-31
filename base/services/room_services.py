from base.models import Room,UserProfile
from typing import List,Dict
from base.services.user_services import profile_pic_url_builder
from django.contrib.auth.models import User
from base.logger import logger

def get_room_name(room_id:int)->str:
    room=Room.objects.get(id=room_id)
    return room.name

def get_room_by_id(room_id:int)->Room:
    return Room.objects.get(id=room_id)


def get_room_member_list(room_id:int)->List[Dict]:
    try:
        room=Room.objects.get(id=room_id)
        members=room.members.all()
        lst=[]
        for member in members:
            dct={}
            dct["member_id"]=member.id
            dct["profile_image"]=profile_pic_url_builder(member.profile.profile_pic.url)
            lst.append(dct)
        return lst
    except User.DoesNotExist:
        logger.error("ERROR in getting members NOT exists")
        return []
    
def get_room_moderator(room_id:int)->List[Dict]:
    try:
        lst=[]
        room=Room.objects.get(id=room_id)
        mods=room.moderator.all()
        for mod in mods:
            dct={}
            dct["id"]=mod.id
            dct["status"]=UserProfile.objects.get(id=mod.id).is_online
            dct["username"]=mod.username
            lst.append(dct)
        return lst
    except Exception as e:
        logger.error(f"ERROR in getting moderator:{str(e)}")
        return []
    
def get_online_users_in_room(room_id:int)->int:
    room=Room.objects.get(id=room_id)
    return room.members.count()