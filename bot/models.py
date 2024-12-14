from django.db import models

class Posts(models.Model):
    user_id = models.BigIntegerField(null=True, blank=True, default=None)
    message_id=models.BigIntegerField(unique=True, null=True, blank=True, default=None)
    type=models.CharField(max_length=60)
    category=models.CharField(max_length=60)
    category_pod = models.CharField(max_length=60)
    random_key = models.CharField(max_length=100,unique=True, null=True, blank=True, default=None)







class Telegram_users(models.Model):
    user_id = models.BigIntegerField(unique=True,null=True, blank=True, default=None)
    block=models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)







