from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'users'
urlpatterns = [
    path('', views.index, name='login'),
    path('v_reg/', views.v_reg, name='v_reg'),
    path('create_department/', views.create_department, name='create_department'),
    path('departments/', views.departments, name='departments'),
    path('create_staff/', views.create_staff, name='create_staff'),
    path('staffs/', views.staffs, name='staffs'),
    path('add_visitor_tag/', views.add_visitor_tag, name='add_tags'),


]
