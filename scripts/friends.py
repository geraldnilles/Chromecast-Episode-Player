#!/usr/bin/env python3

import os



# Put the socket into the instance folder
UNIX_SOCKET_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),"..","instance","cast_socket")

obj = ["show","Friends",5]


from multiprocessing.connection import Client
with Client(UNIX_SOCKET_PATH , authkey=b'secret password') as conn:
    conn.send(obj) 
    resp = conn.recv()
    print (resp)



