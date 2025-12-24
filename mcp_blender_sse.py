#!/usr/bin/env python3
"""Connect to Blender MCP via SSE and add a cube"""
import requests
import json
import threading
import time

sse_url = 'http://localhost:9876/sse'
msg_url = 'http://localhost:9876/messages'

def sse_listener():
    """Listen for SSE events"""
    try:
        print("Connecting to SSE endpoint...")
        response = requests.get(sse_url, stream=True, timeout=60)
        print(f"SSE connected: {response.status_code}")

        for line in response.iter_lines():
            if line:
                print(f"SSE: {line.decode('utf-8')[:200]}")
    except Exception as e:
        print(f"SSE Error: {e}")

# Start SSE listener in background
sse_thread = threading.Thread(target=sse_listener, daemon=True)
sse_thread.start()
time.sleep(2)  # Wait for SSE connection

# Now send the execute command
print("\nSending execute_blender_code request...")
execute_payload = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'tools/call',
    'params': {
        'name': 'execute_blender_code',
        'arguments': {
            'code': '''
import bpy

# Clear any existing cubes
for obj in bpy.data.objects:
    if obj.name.startswith("Cube"):
        bpy.data.objects.remove(obj)

# Add new cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "MCP_Cube"

# Add blue material
mat = bpy.data.materials.new(name="CubeMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.5, 0.8, 1.0)
bsdf.inputs["Metallic"].default_value = 0.3
bsdf.inputs["Roughness"].default_value = 0.4

if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

# Frame in viewport
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for region in area.regions:
            if region.type == 'WINDOW':
                override = {'area': area, 'region': region}
                bpy.ops.view3d.view_selected(override)

print(f"SUCCESS: Cube added at {cube.location}")
'''
        }
    }
}

try:
    response = requests.post(msg_url, json=execute_payload, timeout=30)
    print(f"POST Status: {response.status_code}")
    print(f"POST Response: {response.text[:1000]}")
except Exception as e:
    print(f"POST Error: {e}")

# Wait for SSE responses
time.sleep(3)
print("\nDone!")
