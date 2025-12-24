#!/usr/bin/env python3
"""Test Blender MCP connection and add a cube"""
import requests
import json
import time

url = 'http://localhost:9876/messages'

# Step 1: Initialize
print("Initializing MCP connection...")
init_payload = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'initialize',
    'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {},
        'clientInfo': {
            'name': 'claude-code',
            'version': '1.0'
        }
    }
}

try:
    response = requests.post(url, json=init_payload, timeout=5)
    print(f"Init Status: {response.status_code}")
    print(f"Init Response: {response.text[:500]}")
except Exception as e:
    print(f"Init Error: {e}")

# Step 2: List tools
print("\nListing available tools...")
list_tools_payload = {
    'jsonrpc': '2.0',
    'id': 2,
    'method': 'tools/list'
}

try:
    response = requests.post(url, json=list_tools_payload, timeout=5)
    print(f"Tools Status: {response.status_code}")
    print(f"Tools Response: {response.text[:1000]}")
except Exception as e:
    print(f"Tools Error: {e}")

# Step 3: Execute Blender code to add a cube
print("\nAdding cube via Blender...")
execute_payload = {
    'jsonrpc': '2.0',
    'id': 3,
    'method': 'tools/call',
    'params': {
        'name': 'execute_blender_code',
        'arguments': {
            'code': '''
import bpy

# Add cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "MCP_Cube"

# Add material
mat = bpy.data.materials.new(name="CubeMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.5, 0.8, 1.0)

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

print(f"Cube added: {cube.name} at {cube.location}")
'''
        }
    }
}

try:
    response = requests.post(url, json=execute_payload, timeout=30)
    print(f"Execute Status: {response.status_code}")
    print(f"Execute Response: {response.text[:2000]}")
except Exception as e:
    print(f"Execute Error: {e}")
