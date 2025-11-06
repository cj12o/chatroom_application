from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from django.db.models import Q
from logging import info

class Command(BaseCommand):
    help = "Create or update Celery periodic tasks"

    def handle(self, *args, **kwargs):
        interval=IntervalSchedule(
            every= 10,
            period=IntervalSchedule.SECONDS
        )
        interval.save()

        getTsk=PeriodicTask.objects.filter(Q(name="RoomAgent"))
    
        if len(getTsk)<1:
            task=PeriodicTask.objects.create(
                interval=interval,
                name="RoomAgent",
                task="base.tasks.agent_task.start_agent",
                one_off=True
            )
            task.save()
            
            info(f"Periodictask created task : RoomAgent")
        
