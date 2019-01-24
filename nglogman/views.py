from django.template import loader

from django.views.generic import ListView
from django.http import HttpResponse
from django.shortcuts import redirect
import os

# Create your views here.
from . models import Task, LGNode


def TaskListView(request):
    template = loader.get_template('tasks.html')
    context = {
        'task_set': Task.objects.exclude(status='Completed'),
        'scheduled_tasks': Task.objects.filter(status='Scheduled'),
        'in_progress': Task.objects.filter(status='In Progress'),
        'completed_tasks': Task.objects.filter(status='Completed')
    }
    return HttpResponse(template.render(context, request))


def DashboardView(request):
    template = loader.get_template('dashboard.html')
    context = {
        'available_node_set': LGNode.objects.filter(status='Available'),
        'task_set': Task.objects.exclude(status='Completed')
    }
    return HttpResponse(template.render(context, request))


def outputDownload(request, document_root, path=''):
    filePath = os.path.join(document_root, path)
    with open(filePath, 'rb') as f:
        response = HttpResponse(f.read())
        response['content_type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment;filename=' + path
        return response


def NodeListView(request):
    from nglm_grpc.gRPCMethods import checkNodes
    if request.GET.get('refresh'):
        print('checking nodes...')
        checkNodes(LGNode.objects.all())
        return redirect('nodes')
    template = loader.get_template('nodes.html')
    context = {
        'available_node_set': LGNode.objects.exclude(status='Offline'),
        'offline_node_set': LGNode.objects.filter(status='Offline')
    }
    return HttpResponse(template.render(context, request))
