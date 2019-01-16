from . import nglm_pb2
from . import nglm_pb2_grpc
from nglogman.models import LGNode


class ClientServicer(nglm_pb2_grpc.ClientServicer):
    def register(self, request, context):
        res = nglm_pb2.response()
        try:
            if LGNode.objects.filter(hostname__iexact=request.hostname, ip__iexact=request.ipv4).count() == 0:
                LGNode.objects.create(hostname=request.hostname,ip=request.ipv4)
            print('Registered new node. Hostname: ' + request.hostname + ' IP: ' + request.ipv4)
            res.success = True
        except:
            res.success = False
        return res

def addToServer(server):
    # Adds methods to server, called on server start
    nglm_pb2_grpc.add_ClientServicer_to_server(ClientServicer(), server)

