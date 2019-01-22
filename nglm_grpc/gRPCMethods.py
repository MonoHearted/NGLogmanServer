import grpc
import datetime
import sys
import os

from . import nglm_pb2
from . import nglm_pb2_grpc
from nglogman.models import LGNode, Task


class ServerServicer(nglm_pb2_grpc.ServerServicer):
    def register(self, request, context):
        res = nglm_pb2.response()
        try:
            matchedNodes = LGNode.objects.filter(
                hostname__iexact=request.hostname,
                ip__iexact=request.ipv4
            )
            if matchedNodes.count() == 0:
                LGNode.objects.create(hostname=request.hostname,
                                      ip=request.ipv4, port=request.port)
                print('Registered new node. Hostname: ' +
                      request.hostname + ' IP: ' + request.ipv4 +
                      ' Host Port:' + str(request.port))
            else:
                matchedNodes.update(port=request.port)
                print('Returning node. Hostname: ' +
                      request.hostname + ' IP: ' + request.ipv4 +
                      ' Host Port:' + str(request.port))
            res.success = True
        except:
            res.success = False
        return res

    def isAlive(self, request, context):
        res = nglm_pb2.response()
        res.success = True
        return res


def addToServer(server):
    # Adds services to server, called on server start
    nglm_pb2_grpc.add_ServerServicer_to_server(ServerServicer(), server)


def checkNodes(nodes):
    # returns list of ip:port of available nodes
    import time
    start = time.time()
    availableNodes = []
    for node in nodes:
        nodeAddress = node.ip + ':' + str(node.port)
        try:
            channel = grpc.insecure_channel(nodeAddress)
            nglm_pb2_grpc.ServerStub(channel).isAlive(nglm_pb2.query(query=''))
            availableNodes.append(node)
            channel.close()
        except:
            continue
    end = time.time()
    print(end - start)
    updateNodes(availableNodes)
    return availableNodes


def scheduleTask(task):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        startLogging,
        trigger='date', args=([task.assignedNode], task),
        run_date=task.startTime
    )
    scheduler.start()
    print('Task with UUID ' + str(task.taskUUID) + ' scheduled.')
    return scheduler

def updateNodes(nodes):
    LGNode.objects.all().update(available=False)
    for node in nodes:
        LGNode.objects.filter(ip__iexact=node.ip).update(available=True)


def saveResponse(chunks, path):
    with open(path, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)


def startLogging(nodes, task=None):
    if task is not None:
        Task.objects.filter(taskUUID=task.taskUUID).update(
            status="In Progress")

    for node in nodes:
        nodeAddress = node.ip + ':' + str(node.port)
        try:
            channel = grpc.insecure_channel(nodeAddress)
            stub = nglm_pb2_grpc.LoggingStub(channel)
            params = nglm_pb2.params(pname='httpd', interval=2, duration=4)

            response = stub.start(params)
            resTime = str(datetime.datetime.now())
            saveResponse(response, os.path.join(
                    os.path.dirname(sys.modules['__main__'].__file__),
                    "Output",
                    node.hostname + '_' + str(task.taskUUID) + '_result.xls'))

            if task is not None:
                Task.objects.filter(taskUUID=task.taskUUID).update(
                    status="Completed")
        except:
            print(str(node) + ' was not available for task.')
            continue
