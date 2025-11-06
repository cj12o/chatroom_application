from django.apps import AppConfig
from concurrent.futures.thread import ThreadPoolExecutor
import schedule
import time
from datetime import datetime,date
import os
import asyncio

from logging import info
from django.db.models import Q
# exec=ThreadPoolExecutor(max_workers=12)

# def helper():
#     print("helper called")
#     from .models.message_model import Message
#     from .models.room_model import Room
#     from django.db.models import Q
#     # from .views.agent.room_agent import main

#     from ..core.celery import main

#     from  .views.admin_views import LoginApiview
#     from .views.agent.testSocket import connectTows

#     """todo : index creaed for fast query"""


#     room_lst=Room.objects.all().values('id')
#     print(f"Room lst:{room_lst}")
#     for room in room_lst:
#         id=room["id"]
#         print(f"id:{id}")
#         msg=Message.objects.filter(Q(room__id=id)).order_by('-created_at')
#         if len(msg)<1: continue
#         msg=msg[0]
#         print(f"Msg:{msg.message}")
#         lst=str(msg.created_at).split(".")
#         parsed_date=datetime.strptime(lst[0],"%Y-%m-%d %H:%M:%S")
#         hour_diff=datetime.now().hour-parsed_date.hour
#         print(f"HOUR DIFF=>{hour_diff}")
#         if hour_diff>0 or hour_diff<=0:

#             login_obj=LoginApiview()
#             dct_info={
#                 "email":"agent@email.com",
#                 "password":"agenticqwert4"
#             }
#             print(f"AGENT TO BE TRIGGERED in room :{msg.room.name}")
#             exec.submit(login_obj.post,dct_info)
#             # future=exec.submit(main)
#             result=main.delay()
#             if result.ready():
#                 exec.submit((lambda f: asyncio.run(connectTows(result.get()))))
            




# def job(interval:int=2):
#     """
#     This runs scheduler->
#     after k hours ->last msg mmore than k hrs ago ->agent triggered for room
#     """
#     print("job called")

#     # time.sleep(interval*60*60)
#     time.sleep(interval)
#     exec.submit(helper)
#     exec.submit(job)

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

                