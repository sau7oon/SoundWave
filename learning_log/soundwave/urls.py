from django.urls import path #импортируем инструмент path из Django
from . import views #подключаем файл views.py, в котором находится функция index.

urlpatterns = [ #список адресов сайта 
    path('', views.index, name='index'),
    path('new_topic/', views.new_topic, name='new_topic'),
    path('topics/<int:topic_id>/', views.topic, name='topic'),
    path('topics/<int:topic_id>/new_entry/', views.new_entry, name='new_entry'),
    path('entries/<int:entry_id>/edit/', views.edit_entry, name='edit_entry'), #отвечает какая функция запускается когда polzovatel открывает стр ред конк записи
    path('entries/<int:entry_id>/delete/', views.delete_entry, name='delete_entry'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path(
    'topics/<int:topic_id>/toggle_public/',
    views.toggle_topic_public,
    name='toggle_topic_public'
),
    path('profile/<str:username>/', views.profile, name='profile'), 
    path(
    'topics/<int:topic_id>/delete/',
    views.delete_topic,
    name='delete_topic'
),
]