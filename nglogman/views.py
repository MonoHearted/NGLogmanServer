from django.shortcuts import render
from django.views.generic import ListView

# Create your views here.
from . models import Task,LGNode
class TaskListView(ListView):
    model = Task
    template_name = 'home.html'

class NodeListView(ListView):
    model = LGNode
    template_name = 'nodes.html'