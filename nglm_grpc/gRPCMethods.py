import grpc
import datetime
import os, sys

from . import nglm_pb2
from . import nglm_pb2_grpc
from nglogman.models import LGNode


class ServerServicer(nglm_pb2_grpc.ServerServicer):
    def register(self, request, context):
        res = nglm_pb2.response()
        try:
            matchedNodes = LGNode.objects.filter(hostname__iexact=request.hostname, ip__iexact=request.ipv4)
            if matchedNodes.count() == 0:
                LGNode.objects.create(hostname=request.hostname, ip=request.ipv4, port=request.port)
                print('Registered new node. Hostname: ' + request.hostname + ' IP: ' + request.ipv4
                      + ' Host Port:' + str(request.port))
            else:
                matchedNodes.update(port=request.port)
                print('Returning node. Hostname: ' + request.hostname + ' IP: ' + request.ipv4
                      + ' Host Port:' + str(request.port))
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
    return availableNodes

def saveResponse(chunks, path):
    with open(path, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)

def startLogging(nodes):
    for node in nodes:
        nodeAddress = node.ip + ':' + str(node.port)
        try:
            channel = grpc.insecure_channel(nodeAddress)
            stub = nglm_pb2_grpc.LoggingStub(channel)
            params = nglm_pb2.params(pname='httpd',interval=2,duration=4)

            response = stub.start(params)
            resTime = str(datetime.datetime.now())
            saveResponse(response, os.path.join(
                    os.path.dirname(sys.modules['__main__'].__file__),
                    "Output",
                    node.hostname + '_' + resTime.replace(':', '-').replace('.', '_') + '_result.xls'))
        except:
            raise

