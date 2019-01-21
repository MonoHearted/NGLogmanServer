from django.urls import path
from . import views
from django.http import HttpResponseRedirect

urlpatterns = [
    path('', lambda r: HttpResponseRedirect('dashboard')),
    path('dashboard', views.DashboardView, name='dashboard'),
    path('tasks', views.TaskListView, name='tasks'),
    path('nodes', views.NodeListView, name='nodes'),
]
