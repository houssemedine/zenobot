from django.contrib import admin
from django.urls import path
from matching import views


urlpatterns = [
    path('', views.home,name='matchinghome'),

]
