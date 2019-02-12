from rest_framework import serializers
from .models import LGNode, Task, NodeGroup


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('taskName', 'assignedNode', 'startTime', 'duration',
                  'interval')