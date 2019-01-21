from django.template import loader

from django.views.generic import ListView
from django.http import HttpResponse
from django.shortcuts import redirect

# Create your views here.
from . models import Task, LGNode


def TaskListView(request):
    template = loader.get_template('tasks.html')
    context = {
        'task_set': Task.objects.all()
    }
    return HttpResponse(template.render(context, request))


def DashboardView(request):
    template = loader.get_template('dashboard.html')
    context = {
        'available_node_set': LGNode.objects.filter(available=True),
        'task_set': Task.objects.all()
    }
    return HttpResponse(template.render(context, request))


def NodeListView(request):
    if request.GET.get('refresh'):
        from nglm_grpc.gRPCMethods import checkNodes
        print('checking nodes...')
        checkNodes(LGNode.objects.all())
        return redirect('nodes')
    template = loader.get_template('nodes.html')
    context = {
        'available_node_set': LGNode.objects.filter(available=True),
        'offline_node_set': LGNode.objects.filter(available=False)
    }
    return HttpResponse(template.render(context, request))
