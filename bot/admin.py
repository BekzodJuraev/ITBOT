from django.contrib import admin
from .models import Posts,Telegram_users
@admin.register(Posts)
class Post(admin.ModelAdmin):
    list_display = ['user_id','message_id']
    readonly_fields = ['user_id','message_id']
@admin.register(Telegram_users)
class Post(admin.ModelAdmin):
    list_display = ['user_id','created_at']
