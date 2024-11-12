from django.contrib import admin
from .models import Posts
@admin.register(Posts)
class Post(admin.ModelAdmin):
    list_display = ['user_id','message_id']
    readonly_fields = ['user_id','message_id']
