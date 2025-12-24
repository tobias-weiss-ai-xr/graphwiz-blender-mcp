# GraphWiz Blender MCP Connector

A Model Context Protocol (MCP) connector for Blender that enables bidirectional communication between MCP clients and Blender 3D.

## Overview

This project provides a TCP-based connector that runs inside Blender, allowing external MCP servers to execute Python code and query scene information in real-time. It's designed to work with the [`@glutamateapp/blender-mcp-ts`](https://github.com/ShadowCloneLabs/GlutamateMCPServers) TypeScript server.

## Features

- **TCP Socket Server**: Runs on port 9025 (configurable) to receive commands
- **Python Code Execution**: Safely execute arbitrary Python code in Blender
- **Scene Information**: Query objects, materials, and scene data
- **Object Manipulation**: Create, modify, and delete 3D objects
- **Material Management**: Create and apply materials to objects
- **Viewport Control**: Frame objects and control viewport display

## Installation

### Prerequisites

- Blender 4.0 or later
- Python 3.10+
- Node.js 16+ (for the MCP server)
- `@glutamateapp/blender-mcp-ts` package

### Setup

1. **Clone this repository**:
   ```bash
   git clone https://github.com/yourusername/graphwiz-blender-mcp.git
   cd graphwiz-blender-mcp
   ```

2. **Install the MCP TypeScript server**:
   ```bash
   npm install -g @glutamateapp/blender-mcp-ts
   ```

3. **Configure Claude Code MCP settings**:
   Add to your `.claude/mcp.json`:
   ```json
   {
     "mcpServers": {
       "blender": {
         "command": "node",
         "args": [
           "C:\\Users\\YourUsername\\AppData\\Roaming\\npm\\node_modules\\@glutamateapp\\blender-mcp-ts\\dist\\index.js"
         ],
         "env": {
           "PORT": "9876",
           "CONNECTOR_PORT": "9025"
         }
       }
     }
   }
   ```

## Usage

### Starting the Connector

1. **Open Blender**
2. Go to the **Scripting** workspace
3. Open `blender_mcp_connector.py`
4. Click **Run Script** (▶) or press `Alt+P`

You should see:
```
Blender MCP Connector Started
Listening on localhost:9025
Waiting for MCP server to connect...
```

### Sending Commands

**Option 1: Direct Python Script**

Use `blender_direct_connector.py` to send commands:

```python
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9025))

command = {
    'type': 'execute_blender_code',
    'params': {
        'code': 'import bpy\nbpy.ops.mesh.primitive_cube_add(size=2)'
    }
}

sock.sendall(json.dumps(command).encode('utf-8'))
response = json.loads(sock.recv(4096).decode('utf-8'))
print(response)
```

**Option 2: MCP Server**

The MCP server will automatically connect and provide tools:
- `execute_blender_code` - Execute Python code
- `get_scene_info` - Get scene information
- `get_object_info` - Get specific object details

## Available Commands

### execute_blender_code

Execute arbitrary Python code in Blender:

```json
{
  "type": "execute_blender_code",
  "params": {
    "code": "import bpy\nbpy.ops.mesh.primitive_cube_add(size=2)"
  }
}
```

### get_scene_info

Get information about all objects in the scene:

```json
{
  "type": "get_scene_info",
  "params": {}
}
```

Response:
```json
{
  "status": "success",
  "result": {
    "objects": [
      {
        "name": "Cube",
        "type": "MESH",
        "location": [0.0, 0.0, 0.0],
        "visible": true
      }
    ],
    "object_count": 1
  }
}
```

### get_object_info

Get detailed information about a specific object:

```json
{
  "type": "get_object_info",
  "params": {
    "name": "Cube"
  }
}
```

## Examples

### Add a Colored Cube

```python
code = '''
import bpy

# Add cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object

# Add material
mat = bpy.data.materials.new(name="BlueMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.5, 0.8, 1.0)

cube.data.materials.append(mat)

# Frame in viewport
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for region in area.regions:
            if region.type == 'WINDOW':
                override = {'area': area, 'region': region}
                bpy.ops.view3d.view_selected(override)
'''
```

### Create a Simple Scene

```python
code = '''
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Add light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
bpy.context.active_object.data.energy = 5

# Add camera
bpy.ops.object.camera_add(location=(7, -7, 5))
bpy.context.scene.camera = bpy.context.active_object
'''
```

## Project Structure

```
graphwiz-blender-mcp/
├── blender_mcp_connector.py      # Main connector script (run in Blender)
├── blender_direct_connector.py    # Direct Python client
├── test_cube_simple.py            # Simple test script
├── mcp_blender_test.py            # MCP HTTP test
├── mcp_blender_sse.py             # MCP SSE test
├── add_cube_blender.py            # Standalone cube script
├── README.md                      # This file
└── LICENSE                        # MIT License
```

## Troubleshooting

### Connector not responding

1. Check that Blender is running the connector script
2. Verify port 9025 is not in use: `netstat -an | grep 9025`
3. Check Blender's system console for errors (Window > Toggle System Console)

### "__import__ not found" error

Make sure you're running the latest version of the connector script. Restart Blender completely to clear any cached modules.

### MCP server can't connect

1. Verify the MCP server is configured to use port 9025 for the connector
2. Check that `CONNECTOR_PORT` environment variable is set
3. Ensure the connector is running before starting the MCP server

## Architecture

```
┌─────────────┐      TCP       ┌──────────────┐      HTTP/SSE      ┌──────────┐
│   Blender   │◄──────────────►│   Connector  │◄──────────────────►│ MCP Host │
│             │   Port 9025    │  (in Blender) │     Port 9876      │          │
└─────────────┘                └──────────────┘                    └──────────┘
```

1. **Connector** runs inside Blender on port 9025
2. **MCP Server** (TypeScript) connects to the connector
3. **MCP Client** (Claude Code) connects to the MCP server
4. Commands flow: Client → MCP Server → Connector → Blender

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on work by [Siddharth Ahuja](https://github.com/ahujasid/blender-mcp)
- Built to work with [`@glutamateapp/blender-mcp-ts`](https://github.com/ShadowCloneLabs/GlutamateMCPServers)
- Part of the [GraphWiz](https://graphwiz.ai) ecosystem

## Related Projects

- [GraphWiz](https://graphwiz.ai) - Knowledge graph visualization
- [Neo4j GraphWiz MCP](https://github.com/yourusername/neo4j-graphwiz) - Neo4j MCP server
- [@glutamateapp/blender-mcp-ts](https://github.com/ShadowCloneLabs/GlutamateMCPServers) - TypeScript MCP server for Blender
