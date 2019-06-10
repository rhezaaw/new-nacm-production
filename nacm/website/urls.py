from django.urls import path, re_path
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('config/code_based', views.config_codeBased.as_view(), name="config/code_based"),
    path('config/routing_static', views.config_static.as_view(), name="config/routing_static"),
    path('config/routing_dynamic', views.config_dynamic.as_view(), name="config/routing_dynamic"),
    path('config/routing_bgp', views.config_bgp.as_view(), name="config/routing_bgp"),
    path('config/vlan', views.vlan.as_view(), name="config/vlan"),
    path('restore', views.restore, name="restore"),
    path('backup', views.backup, name="backup"),
    path('setting', views.Settings_display, name="setting/display"),
    path('setting/edit/<int:pk>', views.Settings_edit, name="setting/edit"),
    path('setting/delete/<int:pk>', views.Settings_delete, name="setting/delete"),
    path('setting/add', views.Settings_add, name="setting/add"),
    path('history', views.history, name="history"),
    path('ip_validation', views.ip_validation),
    path('api/login/', views.LoginInfo.as_view()),
    path('api/login/<int:pk>/', views.LoginInfoDetail.as_view()),
    path('api/ip/', views.IpInfo.as_view()),
    path('api/ip/<int:pk>/', views.IpInfoDetail.as_view()),
    path('api/data/', views.DataInfo.as_view()),
 ] 
