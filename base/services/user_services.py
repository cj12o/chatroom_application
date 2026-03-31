from django.conf import settings

from base.models.userprofile_model import UserProfile


def build_absolute_media_url(file_field) -> str | None:
    """Build full URL for any file/image field. Returns None if field is empty."""
    if not file_field:
        return None
    return f"{settings.SITE_BASE_URL}{file_field.url}"


def build_profile_pic_url(profile) -> str | None:
    """Build full URL for a UserProfile's profile pic."""
    if not profile or not profile.profile_pic:
        return None
    return build_absolute_media_url(profile.profile_pic)


def set_user_online_status(username: str, is_online: bool) -> None:
    """Update is_online flag on UserProfile."""
    UserProfile.objects.filter(user__username=username).update(
        is_online=is_online
    )
