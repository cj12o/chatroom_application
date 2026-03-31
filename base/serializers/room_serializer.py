from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import RoomModerationType, Room
from ..models.join_request_model import JoinRequest, RequestStatus

from ..logger import logger
from ..services.room_services import (
    build_member_list_short,
    build_member_list_full,
    build_moderator_list,
    create_room,
    update_room,
)


class RoomSerializerForPagination(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    parent_topic = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    isMember = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    moderation_type = serializers.SerializerMethodField()
    has_pending_request = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_parent_topic(self, obj):
        try:
            return obj.parent_topic.topic
        except Exception as e:
            logger.error(e)

    def get_members(self, obj):
        try:
            return build_member_list_short(obj)
        except Exception as e:
            logger.error(f"ERROR in getting members: {e}")
            return []

    def get_isMember(self, obj) -> bool:
        try:
            user_auth_status = self.context.get("user_auth_status", False)
            if not user_auth_status:
                return False
            return obj.members.filter(username=self.context["username"]).exists()
        except Exception as e:
            logger.error(e)
            return False

    def get_moderator(self, obj):
        try:
            return build_moderator_list(obj)
        except Exception as e:
            logger.error(f"ERROR in getting moderator: {e}")
            return []

    def get_author(self, obj):
        try:
            return {"id": obj.author.id, "name": obj.author.username}
        except Exception as e:
            logger.error(f"ERROR in getting author: {e}")

    def get_tags(self, obj):
        try:
            if len(obj.tags) < 1:
                return []
            return obj.tags
        except Exception as e:
            logger.error(f"ERROR in getting tags: {e}")

    def get_moderation_type(self, obj):
        try:
            return RoomModerationType.get_moderation_type(obj.id)
        except Exception as e:
            logger.error(f"ERROR in getting moderation type: {e}")
            return -2

    def get_has_pending_request(self, obj):
        try:
            if "request" in self.context:
                user = self.context["request"].user
                if user.is_authenticated:
                    return JoinRequest.objects.filter(user=user, room=obj, status=RequestStatus.PENDING).exists()
            elif self.context.get("user_auth_status"):
                user = User.objects.get(username=self.context["username"])
                return JoinRequest.objects.filter(user=user, room=obj, status=RequestStatus.PENDING).exists()
            return False
        except Exception as e:
            logger.error(f"ERROR in getting pending request: {e}")
            return False


class RoomSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    parent_topic = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    moderation_type = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_parent_topic(self, obj):
        return obj.parent_topic.topic

    def get_members(self, obj):
        try:
            return build_member_list_full(obj)
        except User.DoesNotExist:
            return []

    def get_moderator(self, obj):
        return build_moderator_list(obj)

    def get_author(self, obj):
        return {"id": obj.author.id, "name": obj.author.username}

    def get_tags(self, obj):
        if len(obj.tags) < 1:
            return []
        return obj.tags

    def get_moderation_type(self, obj):
        return RoomModerationType.get_moderation_type(obj.id)


class RoomSerializerForCreation(serializers.ModelSerializer):
    moderator = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Room
        fields = ['name', 'description', 'topic', 'is_private', 'moderator', 'tags']

    def create(self, validated_data):
        try:
            moderators = validated_data.pop("moderator", [])
            user = self.context["request"].user
            return create_room(validated_data, user, moderators)
        except Exception as e:
            logger.error(e)

    def update(self, instance, validated_data):
        try:
            return update_room(instance, validated_data)
        except Exception as e:
            logger.error(e)


class RoomSerializerForModeration(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']
