from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.history, name='history'),
    path('players/', views.players, name='players'),
    path('wildbot/', views.players, name='wildbot'),
    url(r'^get_prediction$', views.get_prediction, name='get_prediction'),
]