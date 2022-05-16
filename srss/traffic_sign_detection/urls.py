from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.detect_traffic_sign,name="detect_traffic_sign"),
    path('video_feed1', views.video_feed1, name='video_feed1'),
]
