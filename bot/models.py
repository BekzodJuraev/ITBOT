from django.db import models

class Posts(models.Model):
    user_id = models.BigIntegerField(null=True, blank=True, default=None)
    message_id=models.BigIntegerField(unique=True, null=True, blank=True, default=None)
    category=models.CharField(max_length=255)
    category_pod = models.CharField(max_length=255)




class Telegram_users(models.Model):
    user_id = models.BigIntegerField(unique=True,null=True, blank=True, default=None)





