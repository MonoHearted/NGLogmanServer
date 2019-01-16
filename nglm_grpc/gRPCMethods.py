import grpc

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
        except:
            continue
        else:
            availableNodes.append(nodeAddress)
            channel.close()
    return availableNodes

