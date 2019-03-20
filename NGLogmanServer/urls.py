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
import sys
import threading
from nglm_grpc.gRPCMethods import checkNodes

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nglogman.urls'))
]


# call config and logging module here

# TODO: Expand on 'Failed' Task display (separate page, which failed, log)
# TODO: Clientside Failure Criteria
# TODO: Use pickle real time data streaming to alleviate RAM usage

# add gRPC server start point here
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3.")

if 'runserver' in sys.argv:
    import grpc

    from nglm_grpc.modules.Utility import singletonThreadPool
    from nglm_grpc.gRPCMethods import addToServer, checkNodes
    from nglogman.models import LGNode

    server = grpc.server(singletonThreadPool(max_workers=10))
    addToServer(server)
    server.add_insecure_port('[::]:50051')
    server.start()

    threading.Thread(
        target=checkNodes, kwargs={'repeat': True}
    ).start()
