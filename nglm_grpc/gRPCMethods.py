import grpc
import sys
import os
import uuid
import re
from openpyxl import Workbook, load_workbook

from . import nglm_pb2
from . import nglm_pb2_grpc
from nglogman.models import LGNode, Task

TIMEOUT_SECONDS = 2
ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)

class ServerServicer(nglm_pb2_grpc.ServerServicer):
    def register(self, request, context):
        res = nglm_pb2.registerResponse()
        try:
            matchedNodes = LGNode.objects.filter(
                hostname__iexact=request.hostname,
                ip__iexact=request.ipv4
            )
            if matchedNodes.count() == 0:
                res.uuid = request.uuid if request.uuid else str(uuid.uuid4())
                LGNode.objects.create(hostname=request.hostname,
                                      ip=request.ipv4, port=request.port,
                                      nodeUUID=uuid.UUID(res.uuid))
                print('Registered new node. Hostname: ' +
                      request.hostname + ' IP: ' + request.ipv4 +
                      ' Host Port:' + str(request.port))
            else:
                matchedNodes.update(port=request.port)
                res.uuid = str(matchedNodes[0].nodeUUID)
                print('Returning node. Hostname: ' +
                      request.hostname + ' IP: ' + request.ipv4 +
                      ' Host Port:' + str(request.port))
            res.success = True
        except Exception as e:
            res.success = False
            raise e
        return res

    def isAlive(self, request, context):
        res = nglm_pb2.response()
        res.success = True
        return res


class LoggingServicer(nglm_pb2_grpc.LoggingServicer):
    def output(self, request, context):
        res = nglm_pb2.response()
        try:
            metadata = context.invocation_metadata()
            node_uuid = uuid.UUID(metadata[0].value)
            node = LGNode.objects.filter(nodeUUID=node_uuid)[0]
            task = Task.objects.filter(taskUUID=node.currentTask)[0]

            saveResponse(request, os.path.join(
                ROOT_DIR,
                "Output", str(task.taskUUID),
                node.hostname + '_' + str(task.taskUUID) + '_result.xlsx'))

            Task.objects.filter(taskUUID=task.taskUUID).update(
                status="Completed")
            LGNode.objects.filter(nodeUUID=node.nodeUUID).update(
                status="Available", currentTask=None)
            res.success = True
            validateTask(task)
        except:
            res.success = False
        return res


def addToServer(server):
    # Adds services to server, called on server start
    nglm_pb2_grpc.add_ServerServicer_to_server(ServerServicer(), server)
    nglm_pb2_grpc.add_LoggingServicer_to_server(LoggingServicer(), server)


def validateTask(task):
    output_path = os.path.join(ROOT_DIR, "Output", str(task.taskUUID))
    for node in task.assignedNode.nodes.all():
        path = os.path.join(
            output_path,
            node.hostname + '_' + str(task.taskUUID) + '_result.xlsx'
        )
        if not os.path.isfile(path):
            return False

    res_path = os.path.join(output_path, 'overview.xlsx')
    wb = Workbook()
    for root, dirs, files in os.walk(output_path):
        for f in files:
            name = re.compile(r'(.*)_.*_(?:result.xlsx)').match(f).group(1)
            wb.create_sheet(name, 0)
            read_wb = load_workbook(os.path.join(root, f))
            read_ws = read_wb.worksheets[0]
            for row in read_ws:
                for cell in row:
                    wb.active[cell.coordinate].value = cell.value
    del wb['Sheet']  # removes extra default sheet
    wb.save(res_path)

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
            uuidAttr = str(node.nodeUUID).replace('-', '_')
            if hasattr(checkNodes, uuidAttr):
                retries = getattr(checkNodes, uuidAttr)
                if retries >= 10:
                    LGNode.objects.filter(nodeUUID=node.uuid).delete()
                    # Todo: Implement on_delete to remove assigned tasks
                    delattr(checkNodes, uuidAttr)
                else:
                    setattr(checkNodes, uuidAttr, retries + 1)
            else:
                setattr(checkNodes, uuidAttr, 1)
            continue
    end = time.time()
    print('Available nodes updated. Elapsed: %.2fs' % (end - start))
    updateNodes(availableNodes)
    return availableNodes


def scheduleTask(task):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(
        startLogging,
        trigger='date', args=(task.assignedNode.nodes.all(), task),
        run_date=task.startTime, id=str(task.taskUUID)
    )
    scheduler.start()
    print('Task with UUID %s scheduled.' % task.taskUUID)
    return scheduler, job

def updateNodes(nodes):
    LGNode.objects.exclude(status="Busy").update(status="Offline")
    for node in nodes:
        LGNode.objects.exclude(status="Busy")\
            .filter(ip__iexact=node.ip).update(status="Available")


def saveResponse(chunks, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)
        print('saved to %s' % path)


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
            task.assignedNode.currentTask = task.taskUUID
            task.assignedNode.save()
            Task.objects.filter(taskUUID=task.taskUUID).update(
                status="In Progress")
            LGNode.objects.filter(nodeUUID=node.nodeUUID).update(
                status="Busy", currentTask=task.taskUUID)
        except Exception as e:
            Task.objects.filter(taskUUID=task.taskUUID).update(
                status="Failed: %s" % e)
            print(str(node) + ' was not available for task.')
            continue

def getChunks(f):
    while True:
        chunk = f.read(1024)
        if not chunk:
            break
        yield nglm_pb2.chunks(buffer=chunk)

def setConfig(nodes, f):
    failedNodes = []
    chunkList = list(getChunks(f))
    for node in nodes:
        nodeAddress = node.ip + ':' + str(node.port)
        try:
            iterator = iter(chunkList)
            channel = grpc.insecure_channel(nodeAddress)
            stub = nglm_pb2_grpc.LoggingStub(channel)
            response = stub.setConfig(iterator)
            if not response.success:
                failedNodes.append(node.ip)
        except:
            failedNodes.append(node.ip)
            continue
    return failedNodes

def getConfig(node, size=1):
    nodeAddress = node.ip + ':' + node.port
    channel = grpc.insecure_channel(nodeAddress)
    stub = nglm_pb2_grpc.LoggingStub(channel)
    params = nglm_pb2.chunkSize(size=size)

    response = stub.getConfig(params)
    saveResponse(response, os.path.join(
        os.path.dirname(sys.modules['__main__'].__file__),
        "nodeConfigs", node.nodeUUID + '_config.ini'))
