================
NGLogman Server
================

Overview
--------
This is the server-side component of the NGLogman tool. The main purpose is to manage NGLogman Clients,
by providing features such as grouping, task delegation, configuration setting, etc. It provides these
services through two main ways: a Django-powered web UI, as well as a RESTful API. Server-client
communication uses the gRPC protocol.

Usage
------
To start the server, run the following::

    python3 manage.py runserver $IP:$PORT

This will start the Django webserver, listening on the provided IP and port. The RESTful API shares
this IP and port setting, and can be accessed by the ``/api/`` endpoint. This also starts the
gRPC server used for Server-Client communication, which defaults to ``[::]:50051``. This can be
changed in the file ``NGLogmanServer/urls.py`` in the project directory.

Development Notes
-----------------
If any changes are made to the Django models, it is very important to run migrations before starting
the server::

    python3 manage.py makemigrations
    python3 manage.py migrate

If changes are made to the protobufs, it is important to regenerate the code found in the
``nglm_grpc`` folder::

    python3 -m grpc_tools.protoc -I proto --python_out=./ --grpc_python_out=./ protos/nglm_grpc/nglm.proto

Note that the proto file changes and the regeneration must be done on both the server and the client.


Framework References
--------------------
    - `Django Documentation <https://docs.djangoproject.com/en/2.1/>`_ (ver 2.1)
        See here for documentation regarding the Django webserver, including Database models,
        migrations, templating, etc.
    - `Django Rest Framework <https://www.django-rest-framework.org/>`_
        The Django Rest Framework (DRF) is used for the RESTful API provided by this tool. It provides
        a browsable UI for the API (located at ``/api/``), as well as providing documentation for
        the endpoints.
    - `gRPC Python Documentation <https://grpc.io/grpc/python/>`_
        The gRPC Python API Reference documents the server-client communication protocol used
        in NGLogman Server.
    - `Protobuf Reference <https://developers.google.com/protocol-buffers/>`_
        Google's Protocol Buffer (Protobuf) system is used by gRPC for the auto-generated code.
        The protobufs used in this project can be found under the ``protos`` folder.

Creator
-------
Bryan Niu (b3niu@edu.uwaterloo.ca)