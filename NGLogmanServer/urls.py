"""NGLogmanServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import time
import os,sys

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nglogman.urls'))
]


# call config and logging module here

# add gRPC server start point here
if 'runserver' in sys.argv:
    import grpc

    from nglm_grpc.modules.Utility import singletonThreadPool
    from nglm_grpc.gRPCMethods import addToServer, checkNodes, startLogging
    from nglogman.models import LGNode

    server = grpc.server(singletonThreadPool(max_workers=10))
    addToServer(server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('gRPC server now listening on port 50051\n')

    # Health check testing, wait for clients to connect
    time.sleep(10)
    availableNodes = checkNodes(LGNode.objects.all())

    nodestr = 'Available nodes: '
    for node in availableNodes:
        nodestr = nodestr + str(node)
        if(node != availableNodes[-1]):
            nodestr = nodestr + ', '
    print(nodestr)

    startLogging(availableNodes)

