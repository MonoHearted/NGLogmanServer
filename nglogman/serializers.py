from rest_framework import serializers
from .models import LGNode, Task, NodeGroup
from nglm_grpc.gRPCMethods import scheduleTask
import uuid


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('taskName', 'assignedNode', 'startTime', 'duration',
                  'interval')

    def create(self, validated_data):
        instance = super().create(validated_data)
        scheduleTask(instance)
        return instance

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        scheduleTask(instance)
        return instance


class TaskViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('taskName', 'status', 'assignedNode', 'createTime',
                  'startTime', 'duration', 'interval', 'taskUUID')
        depth = 1


class NodeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LGNode
        fields = ('hostname', 'ip', 'port', 'status', 'currentTask',
                  'comments', 'nodeUUID')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeGroup
        fields = ('id', 'groupname', 'currentTask', 'comments', 'nodes')


class GroupDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeGroup
        fields = ('id', 'groupname', 'currentTask', 'comments', 'nodes')
        depth = 1


