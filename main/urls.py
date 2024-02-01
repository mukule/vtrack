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
    path('v_history/', views.v_history, name='v_history'),
    path('vp/', views.vp, name='vp'),
    path('create_vp/', views.create_vp, name='create_vp'),
    path('rate_visitor/<int:visitor_id>/', views.rate_visitor, name='rate_visitor'),
     path('ro/', views.ro, name='ro'),
    path('create_ro/', views.create_ro, name='create_ro'),
    path('r_success/', views.r_success, name='r_success'),
   

]
