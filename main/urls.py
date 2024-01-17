from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



app_name = 'main'
urlpatterns = [
    path('index', views.dashboard, name='index'),
    path('success/<int:visitor_id>/', views.success, name='success'),
    path('checkins', views.checkins, name='checkins'),
   
]
