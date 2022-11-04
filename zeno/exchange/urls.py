from django.contrib import admin
from django.urls import path
from exchange import views


urlpatterns = [
    path('', views.home,name='exchangehome'),
    path('traitement', views.traitement,name='exchangetraitement'),

]
