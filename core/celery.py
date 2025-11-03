import os
from celery import Celery
from django.db.models  import signals,Q
from django.dispatch import receiver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


app=Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


# @app.task
# def queue_msg():
#     @receiver(signals.post_save,sender=Message)
        
