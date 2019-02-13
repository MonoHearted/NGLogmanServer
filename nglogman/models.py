from django.db import models
import uuid

class LGNode(models.Model):
    """
    A data model map a task entity to db
    """
    hostname = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=50051)
    currentTask = models.UUIDField(null=True, editable=False)
    comments = models.TextField(default='')
    status = models.CharField(max_length=20,
                              editable=False, default='Offline')
    nodeUUID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                null=False, editable=True)

    def __str__(self):
        return str(self.ip) + ":" + str(self.port)

    class Meta:
        verbose_name = 'Logman Node'
        verbose_name_plural = 'Logman Nodes'


class NodeGroup(models.Model):
    groupname = models.CharField(max_length=200)
    currentTask = models.UUIDField(null=True, editable=False)
    comments = models.TextField(default='', blank=True)
    nodes = models.ManyToManyField(LGNode)

    def __str__(self):
        return self.groupname


class Task(models.Model):
    taskName = models.CharField(max_length=200, null=False)
    status = models.CharField(max_length=20,
                              editable=False, default='Scheduled')
    assignedNode = models.ForeignKey(NodeGroup, on_delete=models.CASCADE)
    createTime = models.DateTimeField(auto_now=True)
    startTime = models.DateTimeField(null=False)
    duration = models.DurationField(null=False)
    interval = models.PositiveSmallIntegerField(default=4)
    taskUUID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                editable=False)

    def __str__(self):
        return self.taskName
