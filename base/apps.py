from django.apps import AppConfig
from concurrent.futures.thread import ThreadPoolExecutor
import schedule
import time
from datetime import datetime,date
import os
import asyncio

from logging import info
from django.db.models import Q

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    # def ready(self):
    #     from base.tasks.moderation_task import load_model          