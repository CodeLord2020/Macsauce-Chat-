from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:uid>/<str:token>/', views.reset_password, name='reset_password'),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),


    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),

    path('myinbox/', views.myinbox, name="myinbox"),
    path('messages/<str:username>/', views.direct_message, name='direct_messages'),
    path('deleteDirectMessage/<int:pk>/<str:chattee>', views.deleteDirectMessage, name="deleteDirectMessage"),
]
