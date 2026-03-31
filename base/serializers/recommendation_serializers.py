from rest_framework import serializers
from ..models.recommendation_model import Recommend
from ..services.room_services import build_member_list_full, build_moderator_list
from ..logger import logger


class RecommndationSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    parent_topic = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    reason = serializers.CharField()
    is_private = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    isMember = serializers.SerializerMethodField()

    class Meta:
        model = Recommend
        fields = "__all__"

    def get_id(self, obj):
        return obj.room.id

    def get_author(self, obj):
        return {"id": obj.room.author.id, "name": obj.room.author.username}

    def get_parent_topic(self, obj):
        return obj.room.parent_topic.topic

    def get_members(self, obj):
        return build_member_list_full(obj.room)

    def get_moderator(self, obj):
        return build_moderator_list(obj.room)

    def get_name(self, obj):
        return obj.room.name

    def get_description(self, obj):
        return obj.room.name

    def get_topic(self, obj):
        return obj.room.topic

    def get_is_private(self, obj):
        return obj.room.is_private

    def get_created_at(self, obj):
        return obj.room.created_at

    def get_updated_at(self, obj):
        return obj.room.updated_at

    def get_tags(self, obj):
        return obj.room.tags

    def get_isMember(self, obj):
        try:
            user_auth_status = self.context.get("user_auth_status", False)
            if not user_auth_status:
                return False
            username = self.context.get("username", "")
            return obj.room.members.filter(username=username).exists()
        except Exception as e:
            logger.error(f"ERROR in getting isMember: {e}")
            return False
