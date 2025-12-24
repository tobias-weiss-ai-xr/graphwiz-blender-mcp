#!/usr/bin/env python3
"""Simple test - send cube command to Blender"""
import socket
import json

code = """import bpy
bpy.ops.mesh.primitive_cube_add(size=2)
"""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    sock.connect(('localhost', 9025))
    command = {'type': 'execute_blender_code', 'params': {'code': code}}
    sock.sendall(json.dumps(command).encode('utf-8'))

    data = b''
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        data += chunk
        try:
            response = json.loads(data.decode('utf-8'))
            print("Response:", json.dumps(response, indent=2))
            break
        except json.JSONDecodeError:
            continue
finally:
    sock.close()
