from django.db import models
import uuid

class LGNode(models.Model):
    """
    A data model map a task entity to db
    """
    hostname = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    comments = models.TextField(default='')
    nodeUUID = models.UUIDField(primary_key=True,default=uuid.uuid4(),null=False,editable=True)

    def __str__(self):
        return self.hostname

    class Meta:
        verbose_name = 'Logging Node'
        verbose_name_plural = 'Logging Nodes'


class Task(models.Model):
    taskName = models.CharField(max_length=200,null=False)
    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    createTime = models.DateTimeField(auto_now=True)
    startTime = models.DateTimeField(null=False)
    duration = models.DurationField(null=False)
    interval = models.PositiveSmallIntegerField(default=4)
    taskUUID=models.UUIDField(primary_key=True,
                              default=uuid.uuid4,
                              editable=False)

    def __str__(self):
        return self.taskName
