from django.contrib import admin
from django.urls import path, include
from login import views

urlpatterns = [

    # path('control/', admin.site.urls),

    path('index/', views.index),

    path('login/', views.login),

    path('register/', views.register),

    path('logout/', views.logout),
    path('confirm/', views.user_confirm),

]
