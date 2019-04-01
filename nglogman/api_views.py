from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django.http import Http404

from nglogman.serializers import *
from nglogman.models import Task, LGNode, NodeGroup
from nglm_grpc.gRPCMethods import SCHEDULER

"""
Contains the views and API methods for the RESTful interface of NGLogmanServer.
"""

@api_view(['GET'])
def api_root(request):
    return Response({
        'tasks': reverse('api-task', request=request),
        'nodes': reverse('api-node', request=request),
        'groups': reverse('api-group', request=request)
    })


class TaskInterface(APIView):
    """
    ##GET

    Returns a list of all tasks, including completed ones.

    For a specific task, use the ``/api/tasks/<UUID>`` endpoint.

    ##POST <small>Fields: `taskName`, `assignedNode`, `startTime`, `duration`, `interval`</small>

    Create and schedule a new task.

    """
    parser_classes = (JSONParser,)

    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskViewSerializer(tasks, many=True, read_only=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeInterface(APIView):
    """
    ##GET

    Returns a list of all registered nodes.

    For a specific node, use the ``/api/nodes/<UUID>`` endpoint.
    """
    parser_classes = (JSONParser,)

    def get(self, request):
        nodes = LGNode.objects.all()
        serializer = NodeViewSerializer(nodes, many=True, read_only=True)
        return Response(serializer.data)


class GroupInterface(APIView):
    """
    ##GET

    Returns a list of all node groups.

    For a specific group, use the ``/api/groups/<id>`` endpoint.

    ##POST <small>Fields: `groupname`, `currentTask`, `comments`, `nodes`</small>

    Create and schedule a new group.

    """
    parser_classes = (JSONParser,)

    def get(self, request):
        groups = NodeGroup.objects.all()
        serializer = GroupSerializer(groups, many=True, read_only=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskView(APIView):
    """
    ##GET

    Returns information about this task.

    ##DELETE

    Deletes this task.
    """
    parser_classes = (JSONParser,)

    def get_object(self, pk):
        try:
            pk = uuid.UUID(pk)
            return Task.objects.get(taskUUID=pk)
        except Task.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        task = self.get_object(pk)
        serializer = TaskViewSerializer(task, read_only=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        import apscheduler.jobstores.base as base
        task = self.get_object(pk)

        try:
            SCHEDULER.remove_job(str(task.taskUUID))
        except base.JobLookupError:
            pass

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NodeView(APIView):
    """
    ##GET

    Returns information about this node.

    ##DELETE

    Deletes this node.
    """
    parser_classes = (JSONParser,)

    def get_object(self, pk):
        try:
            pk = uuid.UUID(pk)
            return LGNode.objects.get(nodeUUID=pk)
        except LGNode.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        node = self.get_object(pk)
        serializer = NodeViewSerializer(node, read_only=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupView(APIView):
    """
    ##GET

    Returns information about this group.

    ##DELETE

    Deletes this group.
    """
    parser_classes = (JSONParser,)

    def get_object(self, pk):
        try:
            return NodeGroup.objects.get(pk=pk)
        except NodeGroup.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        group = self.get_object(pk)
        serializer = GroupDetailedSerializer(group, read_only=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
