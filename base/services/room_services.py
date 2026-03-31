from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Prefetch, Q

from base.logger import logger
from base.models import Room, UserProfile, RoomModerationType, Topic
from base.models.Room_Moderation_model import ModerationType
from base.services.user_services import build_profile_pic_url
from base.views.topic_filter import topicsList




def get_room_name(room_id: int) -> str:
    """Return just the room name (single-value query, no joins)."""
    return Room.objects.values_list('name', flat=True).get(id=room_id)


def get_room_by_id(room_id: int) -> Room:
    """Fetch a single room with author & parent_topic pre-loaded."""
    return Room.objects.select_related('author', 'parent_topic').get(id=room_id)


def get_room_queryset(filters: Q = Q(), ordering=None):
    """
    Return a Room queryset with members and moderators prefetched
    (including their profiles). Pass this to serializers
    SerializerMethodFields don't trigger extra queries.
    """
    qs = Room.objects.select_related('author', 'parent_topic').prefetch_related(
        Prefetch('members', queryset=User.objects.select_related('profile')),
        Prefetch('moderator', queryset=User.objects.select_related('profile')),
    )

    if filters:
        qs = qs.filter(filters)
    if ordering:
        qs = qs.order_by(*ordering)
    return qs



def build_member_list_short(room) -> list[dict]:
    """
    Compact member list used by RoomSerializerForPagination.
    Returns: [{"member_id": int, "profile_image": str|None}, ...]
    Assumes room.members is already prefetched with profile.
    """
    return [
        {
            "member_id": member.id,
            "profile_image": build_profile_pic_url(member.profile) if hasattr(member, 'profile') else None,
        }
        for member in room.members.all()
    ]


def build_member_list_full(room) -> list[dict]:
    """
    Detailed member list used by RoomSerializer & RecommndationSerializer.
    Returns: [{"member_id", "member_name", "status", "profile_image"}, ...]
    """
    return [
        {
            "member_id": member.id,
            "member_name": member.username,
            "status": member.profile.is_online if hasattr(member, 'profile') else False,
            "profile_image": build_profile_pic_url(member.profile) if hasattr(member, 'profile') else None,
        }
        for member in room.members.all()
    ]


def build_moderator_list(room) -> list[dict]:
    """
    Moderator list used by all room serializers.
    Returns: [{"id", "username", "status"}, ...]
    Assumes room.moderator is already prefetched with profile.
    """
    return [
        {
            "id": mod.id,
            "username": mod.username,
            "status": mod.profile.is_online if hasattr(mod, 'profile') else False,
        }
        for mod in room.moderator.all()
    ]




def get_online_users(room_id: int) -> list:
    """
    Returns [[username, id, is_online], ...] for all members of a room.
    Single query with prefetch.
    """
    room = Room.objects.prefetch_related(
        Prefetch('members', queryset=User.objects.select_related('profile'))
    ).get(id=room_id)
    return [
        [u.username, u.id, u.profile.is_online if hasattr(u, 'profile') else False]
        for u in room.members.all()
    ]

def create_room(validated_data: dict, user, moderators: list[int]) -> Room:
    """
    Create a room with its moderation type and moderator assignments.
    `moderators` list convention:
      - first element < 0 means non-manual: -1 = semi-auto, -2 = auto
      - first element >= 0 means manual moderation, all IDs are moderator user IDs
    """
    main_topic = topicsList(validated_data["topic"])
    parent_topic = Topic.objects.get(topic=main_topic)

    with transaction.atomic():
        room = Room.objects.create(
            author=user,
            **validated_data,
            parent_topic=parent_topic,
        )

        if moderators[0] < 0:
            if moderators[0] == -1:
                RoomModerationType.objects.create(room=room, moderation_type=ModerationType.SemiAuto)
                users = User.objects.filter(id__in=moderators[1:])
                room.moderator.set(users)
            elif moderators[0] == -2:
                RoomModerationType.objects.create(room=room, moderation_type=ModerationType.Auto)
        else:
            RoomModerationType.objects.create(room=room, moderation_type=ModerationType.Manual)
            users = User.objects.filter(id__in=moderators)
            room.moderator.set(users)
            room.members.add(user)
            room.save()

    return room


def update_room(instance: Room, validated_data: dict) -> Room:
    """
    Update room fields, topic, and moderation settings.
    """
    for attr, v in validated_data.items():
        if attr not in ["id", "moderator", "topic"]:
            setattr(instance, attr, v)

    if "topic" in validated_data:
        parent_topic = topicsList(validated_data["topic"])
        parent_topic_obj = Topic.objects.get(topic=parent_topic)
        instance.parent_topic = parent_topic_obj
        instance.topic = validated_data["topic"]

    if "moderator" in validated_data:
        mods_data = validated_data["moderator"]
        if mods_data[0] < 0:
            instance.moderator.clear()
            if mods_data[0] == -1:
                RoomModerationType.objects.update_or_create(
                    room=instance, defaults={'moderation_type': ModerationType.SemiAuto}
                )
                mods = User.objects.filter(id__in=mods_data[1:])
                instance.moderator.set(mods)
            elif mods_data[0] == -2:
                RoomModerationType.objects.update_or_create(
                    room=instance, defaults={'moderation_type': ModerationType.Auto}
                )
        else:
            RoomModerationType.objects.update_or_create(
                room=instance, defaults={'moderation_type': ModerationType.Manual}
            )
            mods = User.objects.filter(id__in=mods_data)
            instance.moderator.set(mods)

    instance.save()
    return instance
