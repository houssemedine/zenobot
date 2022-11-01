from django.contrib import admin
from django.urls import path
from buffer import views


urlpatterns = [
    path('', views.home,name='bufferhome'),
    path('traitement', views.traitement,name='buffertraitement'),

]
