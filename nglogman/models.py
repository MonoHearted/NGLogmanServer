from django.db import models
import uuid

class LGNode(models.Model):
    """
    A data model map a task entity to db
    """
    hostname = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=50051)
    comments = models.TextField(default='')
    available = models.BooleanField(default=False)
    nodeUUID = models.UUIDField(primary_key=True, default=uuid.uuid4(),
                                null=False, editable=True)

    def __str__(self):
        return str(self.ip) + ":" + str(self.port)

    class Meta:
        verbose_name = 'Logman Node'
        verbose_name_plural = 'Logman Nodes'


class Task(models.Model):
    taskName = models.CharField(max_length=200,null=False)
    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    assignedNode = models.ForeignKey(LGNode, on_delete=models.CASCADE)
    createTime = models.DateTimeField(auto_now=True)
    startTime = models.DateTimeField(null=False)
    duration = models.DurationField(null=False)
    interval = models.PositiveSmallIntegerField(default=4)
    taskUUID = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)

    def __str__(self):
        return self.taskName
