"""
Blender MCP Connector - Run this in Blender first!

This script starts a TCP server on port 9025 that the MCP server connects to.
After running this script, the MCP server on port 9876 will be able to communicate with Blender.

Instructions:
1. Open Blender
2. Go to Scripting tab
3. Create a new text file
4. Paste this script
5. Click Run (or press Alt+P)
6. Leave Blender running - the connector will stay active
"""

import bpy
import socket
import threading
import json
import sys
import builtins

class BlenderMCPConnector:
    """TCP server for Blender MCP connection"""

    def __init__(self, host='localhost', port=9025):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.running = False

    def handle_client(self, client_socket, address):
        """Handle incoming commands from MCP server"""
        self.client_socket = client_socket
        print(f"MCP Client connected from {address}")

        try:
            while self.running:
                # Receive data
                data = b''
                while True:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        return
                    data += chunk
                    try:
                        # Try to parse as JSON
                        message = json.loads(data.decode('utf-8'))
                        break
                    except json.JSONDecodeError:
                        # Need more data
                        continue

                # Process command
                response = self.process_command(message)

                # Send response
                response_data = json.dumps(response).encode('utf-8')
                client_socket.sendall(response_data)

        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            self.client_socket = None
            client_socket.close()
            print("MCP Client disconnected")

    def process_command(self, message):
        """Process a command from the MCP server"""

        command_type = message.get('type')
        params = message.get('params', {})

        print(f"[DEBUG] Connector version 2.0 - Received command: {command_type}")

        try:
            if command_type == 'execute_blender_code':
                # Execute Python code in Blender
                code = params.get('code', '')
                print(f"Executing code: {code[:100]}...")

                # Redirect stdout to capture print statements
                import io
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()

                try:
                    # Provide full builtins for code execution
                    exec(code, {'__builtins__': builtins, 'bpy': bpy})
                    output = sys.stdout.getvalue()
                    result = {'status': 'success', 'output': output}
                except Exception as e:
                    result = {'status': 'error', 'message': str(e)}
                finally:
                    sys.stdout = old_stdout

                return result

            elif command_type == 'get_scene_info':
                # Get scene information
                objects = []
                for obj in bpy.data.objects:
                    objects.append({
                        'name': obj.name,
                        'type': obj.type,
                        'location': list(obj.location),
                        'visible': obj.visible_get()
                    })

                result = {
                    'status': 'success',
 'result': {
                        'objects': objects,
                        'object_count': len(objects)
                    }
                }
                return result

            elif command_type == 'get_object_info':
                # Get specific object info
                obj_name = params.get('name')
                obj = bpy.data.objects.get(obj_name)

                if not obj:
                    return {'status': 'error', 'message': f'Object {obj_name} not found'}

                result = {
                    'status': 'success',
                    'result': {
                        'name': obj.name,
                        'type': obj.type,
                        'location': list(obj.location),
                        'rotation': list(obj.rotation_euler),
                        'scale': list(obj.scale),
                        'visible': obj.visible_get()
                    }
                }
                return result

            else:
                return {'status': 'error', 'message': f'Unknown command: {command_type}'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def start(self):
        """Start the TCP server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.running = True

            print(f"=" * 60)
            print(f"Blender MCP Connector Started")
            print(f"Listening on {self.host}:{self.port}")
            print(f"Waiting for MCP server to connect...")
            print(f"=" * 60)

            # Accept connection in main thread
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, address = self.server_socket.accept()
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Accept error: {e}")

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("Blender MCP Connector stopped")


# Global connector instance
connector = None

def start_connector():
    """Start the MCP connector"""
    global connector
    if connector is None:
        connector = BlenderMCPConnector(port=9025)
        # Start in a separate thread so Blender remains responsive
        thread = threading.Thread(target=connector.start, daemon=True)
        thread.start()
        print("\n✓ MCP Connector is running in Blender")
        print("✓ You can now send commands from the MCP server")
    else:
        print("MCP Connector is already running")

def stop_connector():
    """Stop the MCP connector"""
    global connector
    if connector:
        connector.stop()
        connector = None
        print("MCP Connector stopped")
    else:
        print("No MCP Connector is running")

# Auto-start when script is run
if __name__ == "__main__":
    start_connector()
