from django.contrib import admin
from django.urls import path
from main import views


urlpatterns = [
    path('', views.home,name='zenohome', ),
    # path('', views.home,name='zenohome',  kwargs={'input_type': ''}),
    # path('<slug:input_type>', views.home,name='zenohome'),
]