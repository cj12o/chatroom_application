from django.db import models

class Topic(models.Model):
    topic=models.CharField(unique=True,null=False,blank=False)


