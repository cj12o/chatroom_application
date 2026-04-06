from base.models import Room,Message,Poll,Vote
from django.contrib.auth.models import User
import json
from base.logger import logger
from base.serializers.message_serializer import MessageSerializerForCreation
from django.db.models import Q

def saveMessage(room_id:int,username:str,message:str,parent:int|None=None)->int:
    "saves message to db"
    try:
        room=Room.objects.get(id=room_id)
        author=User.objects.get(username=username)

        msg=Message.objects.create(room=room,author=author,message=message)
        if parent is not None:
            parent_msg=Message.objects.get(id=parent)
            msg.parent=parent_msg
        
        msg.save()
        return msg.id
    except Exception as e:
        logger.error(f"MESSAGE NOT SAVED,error:{str(e)}")
        return -1




def savePoll(room_id:int,username:str,message:str,parent:int|None=None)->int:
    try:
        room=Room.objects.get(id=room_id)
        author=User.objects.get(username=username)
        
        msg=Message.objects.create(room=room,author=author,message="")
        
        if parent is not None:
            parent_msg=Message.objects.get(id=parent)
            msg.parent=parent_msg

        msg.save()

        poll_det=json.loads(message)
        new_poll=Poll.objects.create(message=msg)
        new_poll.question=poll_det["question"]
        new_poll.choices=poll_det={"choices":poll_det["choices"]}
        new_poll.save()
        return msg.id
    except Exception as e:
        logger.error(f"POLL NOT SAVED,error:{str(e)}")
        return -1



def vote_operation(vote_author:str,message_id:int,vote_type:str,room_id:int,status:str)->bool:
    try:
        user=User.objects.get(username=vote_author)
        room=Room.objects.get(id=room_id)
        msg=Message.objects.get(id=message_id)
        # print(f"✅✅status:{status}")
        if status=="subtractVote":
            vote=Vote.objects.get(user__username=user.username,room__name=room.name,message__id=msg.id)
            vote.delete()
            # print("❌deleted vote")
            return True
        else:
            vote_choice=1
            if vote_type=="downvote":
                vote_choice=-1
            vote=Vote.objects.create(user=user,message=msg,room=room,vote=vote_choice)
            # print("✅added vote")
            return True
    except Exception as e:
        logger.error(f"Error in vote operation:{e}")
        return False
    


def get_messages(room_id:int,ascending:bool=False)->list:
    try:
        order = "created_at" if ascending else "-created_at"
        return Message.objects.filter(room_id=room_id).select_related('author__profile','room').order_by(order)
    except Exception as e:
        logger.error(f"Error in getting messages:{e}")
        return []


def get_message_tree(room_id: int) -> dict:
    """
    Reddit-style message tree.
    - Fetches ALL root messages (parent=None), oldest first
    - Builds nested tree in Python
    """

    all_messages = (
        Message.objects
        .filter(room_id=room_id)
        .select_related('author__profile', 'room')
        .order_by('created_at')
    )

    if not all_messages.exists():
        return {"messages": []}

    # Serialize all messages into a flat dict keyed by id
    serializer = MessageSerializerForCreation(all_messages, many=True)
    nodes = {}
    ids = set()
    for item in serializer.data:
        item["children"] = []
        nodes[item["id"]] = item
        ids.add(item["id"])

    # Build tree — attach each child to its parent
    roots = []
    for item in nodes.values():
        parent_id = item.get("parent")
        if parent_id and parent_id in ids:
            nodes[parent_id]["children"].append(item)
        else:
            roots.append(item)

    return {"messages": roots}

def get_lastest_moderated_unsummerized_message(room_id:int,k:int):
    "returns last k messages which are not summerized and are moderated and safe from recent->oldest"
    if k<=0:
        return []
    msgs=Message.objects.filter(Q(room__id=room_id) & Q(messagesummerizedstatus__status=False)&Q(is_moderated=True)&Q(is_unsafe=False)).all()[:k]
    return [msg.message for msg in msgs]
  
    