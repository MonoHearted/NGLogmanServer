from django.urls import path, re_path
from . import views
from django.http import HttpResponseRedirect
from NGLogmanServer.settings import OUTPUT_ROOT, STATICFILES_DIRS

urlpatterns = [
    path('', lambda r: HttpResponseRedirect('dashboard')),
    path('dashboard', views.DashboardView, name='dashboard'),
    path('tasks', views.TaskListView, name='tasks'),
    path('groups', views.GroupListView, name='groups'),
    re_path(r'^groups/(?P<groupID>\d+)/config$', views.ConfigUpload),
    path('nodes', views.NodeListView, name='nodes'),
    re_path(r'^nodeConfigs/(?P<path>.*)$', views.outputDownload,
            {'document_root': STATICFILES_DIRS[0]}),
    re_path(r'^Output/(?P<path>.*)$', views.outputDownload,
            {'document_root': OUTPUT_ROOT})
]