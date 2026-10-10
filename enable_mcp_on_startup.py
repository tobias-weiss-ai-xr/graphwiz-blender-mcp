# Runs once during Blender startup: enable the MCP addon and force server auto-start.
import addon_utils
import bpy

addon_utils.enable("blender_mcp", default_set=True)

import blender_mcp

for s in bpy.data.scenes:
    s.blendermcp_auto_start_server = True

blender_mcp._blendermcp_register_auto_start()
print("GraphWiz: MCP addon enabled, auto-start forced")
