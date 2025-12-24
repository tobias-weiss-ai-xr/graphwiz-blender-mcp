#!/usr/bin/env python3
"""Connect directly to Blender TCP connector on port 9025"""
import socket
import json

def send_blender_command(code):
    """Send command directly to Blender connector"""

    # Connect to Blender
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print("Connecting to Blender connector on port 9025...")
        sock.connect(('localhost', 9025))
        print("Connected!")

        # Prepare command
        command = {
            'type': 'execute_blender_code',
            'params': {
                'code': code
            }
        }

        print(f"Sending command...")
        sock.sendall(json.dumps(command).encode('utf-8'))

        # Receive response
        print("Waiting for response...")
        data = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
            try:
                response = json.loads(data.decode('utf-8'))
                break
            except json.JSONDecodeError:
                continue

        print(f"\nResponse: {json.dumps(response, indent=2)}")
        return response

    finally:
        sock.close()

# Code to add a cube
cube_code = '''
import bpy

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "MCP_Cube"

mat = bpy.data.materials.new(name="CubeMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.5, 0.8, 1.0)

if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for region in area.regions:
            if region.type == 'WINDOW':
                override = {'area': area, 'region': region}
                bpy.ops.view3d.view_selected(override)

result = "SUCCESS: Cube added at " + str(cube.location)
'''

if __name__ == "__main__":
    result = send_blender_command(cube_code)
    if result.get('status') == 'success':
        print("\nSUCCESS: Cube successfully added!")
    else:
        print(f"\nERROR: {result.get('message')}")
