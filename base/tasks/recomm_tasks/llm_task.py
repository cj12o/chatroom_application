from pydantic import BaseModel, Field
from typing import List
import uuid
from celery import shared_task


class RoomFormat(BaseModel):
    room_name: str = Field(description="  room_name")
    room_id: int = Field(description="room_id")
    reason: str = Field(description="reason why this room is recommended")


class RespFormat(BaseModel):
    recommendation: List[RoomFormat]


@shared_task
def Recommend(room_list: list, user_history: list):
    """takes in user history,room_list prompts to llm and returns list of recommended rooms"""

    try:
        from django.conf import settings
        from base.services.llm_services import get_model_with_structed_output
        from base.services.prompt_services import get_prompt
        from base.logger import logger

        room_str = "\n".join(
            f"- room_id: {dct['id']} | room_name: {dct['name']} | description: {dct['document']}"
            for dct in room_list
        )
        user_hist_str = "\n".join(
            f"- room_id: {dct['id']} | room_name: {dct['name']} | description: {dct['description']}"
            for dct in user_history
        )

        systemPrompt = get_prompt("recommend.md")
        humanPrompt = f"""
        Available rooms (List_of_rooms): {room_str}
        User history: {user_hist_str}
        """
        llm = get_model_with_structed_output(settings.OPENAI_MODEL_RECOMMENDATION, RespFormat)

        response = llm.invoke([systemPrompt, humanPrompt])
        print(f"✅✅LLm response:{response}")
        lst = []
        for i in range(0, len(response.recommendation)):
            dct = {}
            dct["name"] = response.recommendation[i].room_name
            dct["id"] = response.recommendation[i].room_id
            dct["reason"] = response.recommendation[i].reason

            lst.append(dct)
        return lst
    except Exception as e:
        from base.logger import logger
        logger.error(e)


@shared_task
def insertRecommInDB(recom_dct: dict, username: str):
    from base.models import Recommend, Room
    from django.contrib.auth.models import User
    from base.logger import logger

    if not recom_dct:
        logger.warning(f"insertRecommInDB received empty/None recommendations for {username}, skipping")
        return

    user = User.objects.get(username=username)
    try:
        for dct in recom_dct:
            try:
                room = Room.objects.get(id=dct["id"])
            except Room.DoesNotExist:
                logger.warning(f"Skipping recommendation for room {dct['id']}: no longer exists")
                continue
            Recommend.objects.create(user=user, room=room, reason=dct["reason"], session=uuid.uuid4())
    except Exception as e:
        logger.error(e)


@shared_task
def orchestrator(username: str, sessioncount: int, per_session_hist_count: int):
    """
    1)get user hist
    2)get cosin sim rooms
    3)recommend(llm)
    4)insert in db

    """
    from .recommend_task import HistList, getCosinSimRooms
    from base.models import Room
    from base.models.recommendation_model import Recommend as RecommendModel
    from .llm_task import insertRecommInDB
    from base.logger import logger
    from django.contrib.auth.models import User
    from base.services.rate_limiter import check_and_increment

    try:
        user = User.objects.get(username=username)

        # Skip if recommendations already exist for this user
        existing = RecommendModel.objects.filter(user=user).first()
        if existing:
            logger.info(f"Fresh recommendations exist for {username}, skipping LLM call")
            return

        # Rate limit check
        if not check_and_increment(user.id, "recommendation"):
            logger.warning(f"Recommendation rate limit hit for user {username}")
            return

        user_history_dict = HistList(username=username, x=sessioncount, k=per_session_hist_count)

        resultant_list = getCosinSimRooms(user_history_dict=user_history_dict)
        if resultant_list is None:
            logger.warning(f"getCosinSimRooms returned None for {username} (ChromaDB unavailable?), skipping recommendation")
            return

        room_list = []
        for k, v in user_history_dict.items():
            for r_id, _ in v.items():
                try:
                    room = Room.objects.get(id=r_id)
                except Room.DoesNotExist:
                    logger.warning(f"Skipping room {r_id}: no longer exists")
                    continue
                room_list.append({"id": r_id, "name": room.name, "description": room.description})

        final_rooms_to_recommend = Recommend(room_list=resultant_list, user_history=room_list)

        insertRecommInDB.delay(final_rooms_to_recommend, username)
    except Exception as e:
        logger.error(e)
