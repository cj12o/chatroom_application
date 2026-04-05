from django.core.management.base import BaseCommand
from base.models import Topic


class Command(BaseCommand):
    help = "Populate the Topic table with default topics"

    def handle(self, *args, **options):
        topics = ["Technology", "Lifestyle"]
        for name in topics:
            obj, created = Topic.objects.get_or_create(topic=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created topic: {name}'))
            else:
                self.stdout.write(f'Topic already exists: {name}')


