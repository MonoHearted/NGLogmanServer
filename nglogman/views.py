from django.template import loader

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
import os

# Create your views here.
from . models import Task, LGNode, NodeGroup
from nglm_grpc.gRPCMethods import setConfig
from django.db.models import Count, Q


def TaskListView(request):
    template = loader.get_template('tasks.html')
    context = {
        'task_set': Task.objects.exclude(status='Completed'),
        'scheduled_tasks': Task.objects.filter(status='Scheduled'),
        'in_progress': Task.objects.filter(status='In Progress'),
        'completed_tasks': Task.objects.filter(status='Completed'),
        'failed_tasks': Task.objects.filter(status__contains='Failed')
    }
    return HttpResponse(template.render(context, request))


def DashboardView(request):
    template = loader.get_template('dashboard.html')
    context = {
        'node_groups': NodeGroup.objects.all().annotate(
            node_count=Count('nodes')
        ),
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


def GroupListView(request):
    template = loader.get_template('groups.html')
    context = {
        'node_groups': NodeGroup.objects.all().annotate(
            node_count=Count('nodes'),
            off_count=Count('nodes', filter=Q(nodes__status__iexact='offline'))
        )
    }
    return HttpResponse(template.render(context, request))


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


def ConfigUpload(request, groupID=''):
    from .forms import ConfigForm
    template = loader.get_template('config.html')
    if request.method == 'POST':
        form = ConfigForm(groupID, request.POST, request.FILES)
        if form.is_valid():
            failedNodes = setConfig(
                NodeGroup.objects.get(id=groupID).nodes.all(),
                request.FILES['file'])
            if not failedNodes:
                messages.success(request, 'Successfully set all configs.')
            else:
                messages.warning(request, 'Failed to set config for: '
                                 + ', '.join(failedNodes))
    else:
        form = ConfigForm(groupID)
    context = {
        'form': form,
        'group_name': NodeGroup.objects.get(id=groupID).groupname,
        'offline_nodes': NodeGroup.objects.get(id=groupID).nodes.filter(
            status__iexact="offline"
        )
    }
    return HttpResponse(template.render(context, request))
