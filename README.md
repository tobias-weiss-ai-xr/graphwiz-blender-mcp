# GraphWiz Blender MCP

Blender ↔ LLM integration for the GraphWiz ecosystem. This repo is the setup/config home for controlling Blender from any MCP client (pi, Claude Code, Cursor, ob.com…).

## What's integrated

The solution is built on **[mcp-for-blender](https://github.com/ahujasid/mcp-for-blender)** (by [Siddharth Ahuja](https://github.com/ahujasid), the author of the original `blender-mcp` this project was based on). It is the de-facto standard Blender MCP server (~30k stars, actively maintained) and subsumes everything the original `@glutamateapp/blender-mcp-ts` connector offered.

**MCP server** (runs via `uvx mcp-for-blender`, stdio): 9 tools

| Tool | Purpose |
|---|---|
| `execute_blender_code` | Run arbitrary Python in your live Blender |
| `get_scene_info` | Compact scene summary, one line per object |
| `look` | **Visual verification** — viewport/camera/multi-angle screenshots, renders, wireframe/xray |
| `generate_3d` | Text/image → 3D via Tripo, Hunyuan3D, Hyper3D Rodin |
| `search_assets` / `import_asset` | Poly Haven, Sketchfab, Poly Pizza, AmbientCG assets |
| `get_addon_status` | Blender + addon version, enabled libraries |
| `disable_telemetry` / `record_trajectory_feedback` | Data controls |

**Blender addon** (installed in Blender, listens on TCP port 9876).

```
┌─────────────┐   stdio (MCP)    ┌──────────────────┐    TCP 9876    ┌──────────┐
│  MCP client │◄────────────────►│ mcp-for-blender  │◄──────────────►│  Blender │
│  pi / etc.  │   uvx mcp-for-blender  │   (FastMCP server)  │  addon (bpy)  │
└─────────────┘                └──────────────────┘                └──────────┘
```

## Setup

Prereqs: Blender 3.0+, [uv](https://docs.astral.sh/uv/), pip's `uv` doesn't count.

### 1. Install the Blender addon

```bash
uvx mcp-for-blender install-addon
# list detected Blender addons folders:
uvx mcp-for-blender addon-paths
```

In Blender: **Edit → Preferences → Add-ons** → enable **Interface: MCP for Blender** (restart Blender if it doesn't show). Then in the 3D viewport sidebar (**N** → **MCP for Blender** tab) click **Start MCP Server**. Or run headless:

```bash
blender --python-expr "import blender_mcp; blender_mcp.start_server()"
```

### 2. Register the MCP server

pi (`~/.pi/agent/mcp.json`) — this repo's machine is already configured:

```json
{
  "mcpServers": {
    "blender": {
      "command": "C:/ProgramData/chocolatey/bin/uvx.exe",
      "args": ["mcp-for-blender"]
    }
  }
}
```

Use the absolute `uvx` path so GUI-launched clients (which don't inherit your terminal PATH) still find it. On a locked-down machine without uv: `pipx install mcp-for-blender` and point the client at that binary instead.

```bash
# Claude Code / Codex:
claude mcp add blender uvx mcp-for-blender
codex mcp add blender -- uvx mcp-for-blender
```

### 3. Update

```bash
uvx mcp-for-blender@latest update   # server + every installed addon copy
```

## Usage examples

```python
# Model something, then see it:
bpy.ops.mesh.primitive_cube_add(size=2)
# look(viewport=...) → screenshot comes back to the model
```

Typical loop: model via `execute_blender_code` → `look` → fix → render → export.

## Ecosystem survey (integrated options considered)

Surveyed GitHub (Nov 2025–2026). One server was adopted to avoid port conflicts (every addon wants 9876) and tool-name collisions:

| Project | Tools | Verdict |
|---|---|---|
| **ahujasid/mcp-for-blender** | 9 core | ✅ **adopted** — de-facto standard, maintained, visual verification + assets + generation |
| ageless-h/blender-mcp | 29 | Good deep-perception API (`blender_` prefix), but alpha-grade; duplicative of the above |
| djeada/blender-mcp-server | 27 | Nice file I/O + async jobs; reimplements what `execute_blender_code` already covers |
| mackson/blender-mcp | 17 | TS + WebSocket bridge; Antigravity-oriented, fewer tools |
| RFingAdam/mcp-blender | 218 | MSFS/engineering niche + AI pipeline; overkill |
| PatrykIti/blender-ai-mcp | ~30 | Goal-first router + vision MLX; complex, cloud dependencies |
| Blender Foundation MCP | — | Official, but Blender 5.1+ only (this machine: 4.0/4.4); llama.cpp-bound |
| Pervaiz106/Blender-Mcp-Server | 47 | 0 stars, unmaintained |

If you need the curated 29-tool `blender_*` surface later, `ageless-h` can be registered as a *second* server (it uses `blender_` prefixes precisely to coexist).

## Legacy (original GraphWiz connector)

`blender_mcp_connector.py` (+ `@glutamateapp/blender-mcp-ts`) is the original hand-rolled TCP connector. It still works but is superseded — it exposed only 8 tools and required a separate TS server. Keep it only if you need the raw port-9025 JSON protocol:

- `blender_mcp_connector.py` — run inside Blender (port 9025)
- `blender_direct_connector.py` / `test_cube_simple.py` — raw TCP clients
- `mcp_blender_sse.py` / `mcp_blender_test.py` — legacy HTTP/SSE probes (port 9876, outdated)
- `add_cube_blender.py` — standalone scene-setup demo

## Troubleshooting

- **Addon won't connect**: confirm Blender's addon shows `Server running on ws://…:9876`. Check `netstat -an | grep 9876`. Only one Blender may own the port.
- **GUI client can't spawn the server**: use the absolute `uvx.exe` path (or `cmd /c uvx …` on Windows) and fully quit/relaunch the client.
- **`uvx` runs an old version**: `uvx mcp-for-blender@latest update` — early releases lacked `update`.
- **Blender 4.0**: works, but `look`/generators want a recent addon — update via the in-Blender sidebar tab.

## License

MIT — see [LICENSE](LICENSE).
