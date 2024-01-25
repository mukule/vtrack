from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'main'
urlpatterns = [
    path('index', views.dashboard, name='index'),
    path('checkin/', views.checkin, name='checkin'),
    path('drivein/', views.drivein, name='drivein'),
    path('verify/<int:visitor_id>/', views.verify, name='verify'),
    path('success/<int:visitor_id>/', views.success, name='success'),
    path('checkins', views.checkins, name='checkins'),
    path('tags/', views.tags, name='tags'),
    path('checkouts/', views.checkouts, name='checkouts'),
    path('checkout_visitor/<int:visitor_id>/',
         views.checkout_visitor, name='checkout_visitor'),
    path('proceed/<int:visitor_id>/', views.proceed, name='proceed'),

]
