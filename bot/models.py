from django.db import models

class Posts(models.Model):
    user_id = models.BigIntegerField(unique=True, null=True, blank=True, default=None)
    message_id=models.BigIntegerField(unique=True, null=True, blank=True, default=None)



    def __str__(self):
        return self.user_id
