from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
import uuid

class LGNode(models.Model):
    """
    A data model that maps a Node entity to database
    """
    hostname = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=50052)
    currentTask = models.UUIDField(null=True, editable=False)
    comments = models.TextField(default='')
    status = models.CharField(max_length=200,
                              editable=False, default='Offline')
    nodeUUID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                null=False, editable=True)

    def __str__(self):
        return str(self.ip) + ":" + str(self.port)

    class Meta:
        verbose_name = 'Logman Node'
        verbose_name_plural = 'Logman Nodes'


class NodeGroup(models.Model):
    """
    A data model that reflects a group of LGNode instances.
    """
    groupname = models.CharField(max_length=200)
    currentTask = models.UUIDField(null=True, editable=False)
    comments = models.TextField(default='', blank=True)
    nodes = models.ManyToManyField(LGNode)

    def __str__(self):
        return self.groupname


class Task(models.Model):
    """
    A data model that maps a Node entity to database
    """
    taskName = models.CharField(max_length=200, null=False)
    status = models.CharField(max_length=200,
                              editable=False, default='Scheduled')
    assignedNode = models.ForeignKey(NodeGroup, on_delete=models.CASCADE,
                                     verbose_name='Assigned Group')
    createTime = models.DateTimeField(auto_now=True)
    startTime = models.DateTimeField(null=False)
    duration = models.DurationField(null=False, help_text='{hh}:{mm}:{ss} or '
                                                          '{%s}')
    interval = models.PositiveSmallIntegerField(default=4, help_text='{%s}')
    taskUUID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                editable=False)

    def __str__(self):
        return self.taskName

    def clean(self):
        super().clean_fields()
        if self.startTime < timezone.now():
            raise ValidationError("Chosen start time has already passed.")

        qs = Task.objects.exclude(Q(status__exact='Completed') |
                                  Q(status__contains='Failed'))
        for task in qs:
            end = task.startTime + task.duration
            if task.startTime <= self.startTime <= end:
                busyNodes = []
                for node in self.assignedNode.nodes.all():
                    if node in task.assignedNode.nodes.all():
                        busyNodes.append(node.ip)
                raise ValidationError("The following nodes are unavailable"
                                      " at the specified time: \n %s"
                                      % ', '.join(busyNodes))
