"""Main entry point for the OBJ visualizer."""
import sys
import os
import glfw
from OpenGL.GL import *

import config
import camera
import loaders
import rendering
import matrix


def main():
    """Main application loop."""
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Usage: python scop.py fichier.obj [optional_texture.bmp]")
        return

    if not glfw.init():
        print("GLFW error")
        return

    window = glfw.create_window(1600, 1200, ".OBJ Visualizer in Python", None, None)
    if not window:
        glfw.terminate()
        print("GLFW error: window creation failed")
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, camera.key_callback)

    glEnable(GL_DEPTH_TEST)

    filename, file_extension = os.path.splitext(sys.argv[1])
    if file_extension.lower() != ".obj":
        print("Error: The first argument must be an .obj file")
        glfw.terminate()
        return

    if not loaders.loadOBJ(sys.argv[1]):
        glfw.terminate()
        return
        
    config.cameraDistance = 5.0
    config.cameraYaw = 0.0
    config.cameraPitch = 0.0

    import math
    config.cameraX = config.targetX + config.cameraDistance * math.sin(config.cameraYaw) * math.cos(config.cameraPitch)
    config.cameraY = config.targetY + config.cameraDistance * math.sin(config.cameraPitch)
    config.cameraZ = config.targetZ + config.cameraDistance * math.cos(config.cameraYaw) * math.cos(config.cameraPitch)

    # load a texture BMP file:
    if len(sys.argv) == 3:
        loaders.loadBMP(sys.argv[2])
        
    camera.print_controls()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        width, height = glfw.get_framebuffer_size(window)
        ratio = width / float(height if height > 0 else 1)

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Custom perspective projection matrix
        proj_matrix = matrix.perspective_matrix(45.0, ratio, 0.1, 100.0)
        glLoadMatrixf(matrix.matrix_to_flat_list(proj_matrix))

        # Custom lookAt view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        view_matrix = matrix.lookAt_matrix((config.cameraX, config.cameraY, config.cameraZ),
                                           (config.targetX, config.targetY, config.targetZ),
                                           (0.0, 1.0, 0.0))
        glMultMatrixf(matrix.matrix_to_flat_list(view_matrix))
        rendering.render()
        glfw.swap_buffers(window)

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
