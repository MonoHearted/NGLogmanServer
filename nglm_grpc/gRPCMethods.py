import grpc
import datetime
import sys
import os

from . import nglm_pb2
from . import nglm_pb2_grpc
from nglogman.models import LGNode, Task

TIMEOUT_SECONDS = 2

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
            checkNodes(LGNode.objects.all())
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
            print('checking: %s' % node)
            channel = grpc.insecure_channel(nodeAddress)
            nglm_pb2_grpc.ServerStub(channel)\
                .isAlive(nglm_pb2.query(query=''), timeout=TIMEOUT_SECONDS)
            print('checked: %s' % node)
            availableNodes.append(node)
            channel.close()
        except:
            continue
    end = time.time()
    print('Available nodes updated. Elapsed: %.2fs' % (end - start))
    updateNodes(availableNodes)
    return availableNodes


def scheduleTask(task):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        startLogging,
        trigger='date', args=(task.assignedNode.all(), task),
        run_date=task.startTime
    )
    scheduler.start()
    print('Task with UUID %s scheduled.' % task.taskUUID)
    return scheduler

def updateNodes(nodes):
    LGNode.objects.exclude(status="Busy").update(status="Offline")
    for node in nodes:
        LGNode.objects.exclude(status="Busy")\
            .filter(ip__iexact=node.ip).update(status="Available")


def saveResponse(chunks, path):
    with open(path, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)


def startLogging(nodes, task):
    for node in nodes:
        nodeAddress = node.ip + ':' + str(node.port)
        try:
            channel = grpc.insecure_channel(nodeAddress)
            stub = nglm_pb2_grpc.LoggingStub(channel)
            itr = task.interval if task.interval else 2
            dur = int(task.duration.total_seconds()) if task.duration else 4
            params = nglm_pb2.params(pname='httpd', interval=itr, duration=dur)

            response = stub.start(params)
            Task.objects.filter(taskUUID=task.taskUUID).update(
                status="In Progress")
            LGNode.objects.filter(nodeUUID=node.nodeUUID).update(
                status="Busy", currentTask=task.taskUUID)
            saveResponse(response, os.path.join(
                    os.path.dirname(sys.modules['__main__'].__file__),
                    "Output",
                    node.hostname + '_' + str(task.taskUUID) + '_result.xls'))

            Task.objects.filter(taskUUID=task.taskUUID).update(
                status="Completed")
            LGNode.objects.filter(nodeUUID=node.nodeUUID).update(
                status="Available", currentTask=None)
        except Exception as e:
            Task.objects.filter(taskUUID=task.taskUUID).update(
                status="Failed: %s" % e)
            print(str(node) + ' was not available for task.')
            continue


def getConfig(node, size=1):
    nodeAddress = node.ip + ':' + node.port
    channel = grpc.insecure_channel(nodeAddress)
    stub = nglm_pb2_grpc.LoggingStub(channel)
    params = nglm_pb2.chunkSize(size=size)

    response = stub.getConfig(params)
    saveResponse(response, os.path.join(
        os.path.dirname(sys.modules['__main__'].__file__),
        "nodeConfigs", node.nodeUUID + '_config.ini'))
