from rest_framework import serializers
from .models import LGNode, Task, NodeGroup
from nglm_grpc.gRPCMethods import scheduleTask
import uuid


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializes API JSON input into Task model data. The assignedNode foreign
    key field is represented by its primary key.
    """
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
    """
    A more detailed serializer for use GET on the Task API. Expands the
    assignedNode foreign key field into a nested JSON object rather than
    primary key.
    """
    class Meta:
        model = Task
        fields = ('taskName', 'status', 'assignedNode', 'createTime',
                  'startTime', 'duration', 'interval', 'taskUUID')
        depth = 1


class NodeViewSerializer(serializers.ModelSerializer):
    """
    Serializes API JSON input into LGNode model data.
    """
    class Meta:
        model = LGNode
        fields = ('hostname', 'ip', 'port', 'status', 'currentTask',
                  'comments', 'nodeUUID')


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializes API JSON input into Group model data. The nodes foreign key
    field is represented by its primary key.
    """
    class Meta:
        model = NodeGroup
        fields = ('id', 'groupname', 'currentTask', 'comments', 'nodes')


class GroupDetailedSerializer(serializers.ModelSerializer):
    """
    A more detailed serializer for use GET on the Group API. Expands the
    nodes foreign key field into a nested JSON object rather than primary key.
    """
    class Meta:
        model = NodeGroup
        fields = ('id', 'groupname', 'currentTask', 'comments', 'nodes')
        depth = 1


