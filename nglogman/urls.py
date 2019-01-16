from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='home'),
    path('nodes', views.NodeListView.as_view(), name='nodes'),
]
