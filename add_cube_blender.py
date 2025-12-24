"""
Add a cube to Blender and verify with screenshot
Run this in Blender's Scripting tab -> New text file -> Run Script
"""

import bpy
import os
import tempfile

def add_cube_and_verify():
    """Add a cube to the scene and capture a screenshot"""

    print("=" * 50)
    print("Adding cube to Blender scene...")
    print("=" * 50)

    # Add a cube
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "Verification_Cube"
    print(f"✓ Created cube: {cube.name}")
    print(f"  Location: {cube.location}")
    print(f"  Dimensions: {cube.dimensions}")

    # Create a material for better visibility
    mat = bpy.data.materials.new(name="Cube_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.2, 0.5, 0.8, 1.0)  # Blue
    bsdf.inputs["Metallic"].default_value = 0.3
    bsdf.inputs["Roughness"].default_value = 0.4

    # Assign material to cube
    if cube.data.materials:
        cube.data.materials[0] = mat
    else:
        cube.data.materials.append(mat)
    print(f"✓ Added material: {mat.name}")

    # Set viewport shading to SOLID for better visibility
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.shading.light = 'STUDIO'
                    space.shading.color_type = 'OBJECT'
    print("✓ Set viewport to SOLID shading")

    # Add lights if none exist
    if not any(obj.type == 'LIGHT' for obj in bpy.data.objects):
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.data.energy = 5
        print("✓ Added sun light")

        bpy.ops.object.light_add(type='POINT', location=(-3, -3, 5))
        point = bpy.context.active_object
        point.data.energy = 500
        print("✓ Added point light")

    # Find or create camera
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(5, -5, 3))
        camera = bpy.context.active_object
        print("✓ Created camera")
    else:
        camera = bpy.data.objects["Camera"]
        print("✓ Using existing camera")

    # Point camera at cube
    direction = cube.location - camera.location
    if direction.length > 0:
        rot_quat = direction.to_track_quat('-Z', 'Y')
        camera.rotation_euler = rot_quat.to_euler()
    print(f"✓ Camera pointing at cube from {camera.location}")

    # Set active camera
    bpy.context.scene.camera = camera

    # Frame the cube in viewport
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_selected(override)
                    break
    print("✓ Framed cube in viewport")

    # Set render settings
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # Use Eevee for fast rendering
    if hasattr(bpy.context.scene.render, 'engine'):
        scene.render.engine = 'BLENDER_EEVEE' if bpy.app.version >= (2, 80, 0) else 'BLENDER_RENDER'

    # Save screenshot to temp directory
    temp_dir = tempfile.gettempdir()
    screenshot_path = os.path.join(temp_dir, "blender_cube_verification.png")
    scene.render.filepath = screenshot_path

    # Render the image
    print(f"\nRendering screenshot to:")
    print(f"  {screenshot_path}")
    bpy.ops.render.render(write_still=True)

    print("\n" + "=" * 50)
    print("✓ SUCCESS! Cube added and verified!")
    print("=" * 50)
    print(f"\nScreenshot saved:")
    print(f"  {screenshot_path}")
    print(f"\nYou can view the screenshot in Blender by:")
    print(f"  1. Going to the Scripting workspace")
    print(f"  2. In the 'Image Editor' panel, go to File > Open")
    print(f"  3. Navigate to: {temp_dir}")
    print(f"  4. Open 'blender_cube_verification.png'")

    return cube, screenshot_path

# Execute the function
if __name__ == "__main__":
    try:
        cube, screenshot = add_cube_and_verify()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
