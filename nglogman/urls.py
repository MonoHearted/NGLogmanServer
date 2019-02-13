from django.urls import include, path, re_path
from . import views
from . import api_views
from django.http import HttpResponseRedirect
from rest_framework import routers
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
    re_path(r'tasks/(?P<taskUUID>.*)/overview$', views.overviewGraph),
    re_path(r'^Output/(?P<path>.*)$', views.outputDownload,
            {'document_root': OUTPUT_ROOT}),

    path('api', api_views.api_root),
    path('api/tasks', api_views.TaskInterface.as_view(), name='api-task'),
    path('api/tasks/<pk>', api_views.TaskView.as_view(), name='api-task-view'),
    path('api/nodes', api_views.NodeInterface.as_view(), name='api-node'),
    path('api/nodes/<pk>', api_views.NodeView.as_view(), name='api-node-view'),
    path('api/groups', api_views.GroupInterface.as_view(), name='api-group'),
    path('api/groups/<pk>', api_views.GroupView.as_view(), name='api-group-view')
]