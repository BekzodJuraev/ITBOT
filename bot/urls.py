from django.urls import path
from . import views


urlpatterns=[
     path('telegram_webhook/', views.webhook, name='webhook'),
     path('',views.index,name='index')

]

