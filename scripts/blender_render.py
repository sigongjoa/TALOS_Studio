import bpy
import sys
import os

def render_model(model_path, output_path, camera_angle):
    """
    Renders a 3D model using Blender.
    This script is intended to be run from within Blender.
    """
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import the model
    bpy.ops.import_scene.gltf(filepath=model_path)

    # Set up the camera
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.location = (0, -5, 0) # Position the camera
    # Point the camera to the origin (where the model is)
    camera.rotation_euler = (1.5708, 0, 0) # 90 degrees in X

    # Set camera angle from arguments
    camera.rotation_euler[0] += camera_angle[0]
    camera.rotation_euler[1] += camera_angle[1]
    camera.rotation_euler[2] += camera_angle[2]

    # Set the scene's camera
    bpy.context.scene.camera = camera

    # Set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024

    # Render the image
    bpy.ops.render.render(write_still=True)

    print(f"Rendered image saved to {output_path}")

if __name__ == "__main__":
    # Blender scripts are often run with arguments passed after --
    argv = sys.argv
    try:
        # Get arguments after --
        args = argv[argv.index("--") + 1:]
        model_path = args[0]
        output_path = args[1]
        # A simple way to pass camera angle, e.g., "30,45,0"
        camera_angle_str = args[2].split(',')
        camera_angle_rad = [float(a) * (3.14159 / 180.0) for a in camera_angle_str]

        render_model(model_path, output_path, camera_angle_rad)

    except (ValueError, IndexError) as e:
        print(f"Error parsing arguments: {e}")
        print("Usage: blender --background --python scripts/blender_render.py -- <model_path> <output_path> <camera_angle_degrees_comma_separated>")
        sys.exit(1)
