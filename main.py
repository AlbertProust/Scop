import sys
import glfw
import os
import math
from OpenGL.GL import *
import state, math_utils, camera, loaders, render


def printControls():
    print("Camera controls :")
    print("  Rotation : W/S/A/D or arrows")
    print("  Zoom     : Q (zoom out) / E (zoom in)")
    print("  Move     : I/K/J/L")
    print("  Quit     : ESC")


def main():
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Usage: python main.py file.obj optional_texture.obj")
        return

    if not glfw.init():
        print("GLFW error")
        return

    window = glfw.create_window(1600, 1200, ".OBJ Visualizer in Python", None, None)
    if not window:
        glfw.terminate()
        print("GLFW error: window creation failed")
        return
    state.window = window

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

    state.cameraYaw = 0.0
    state.cameraPitch = 0.0
    state.cameraDistance = state.obj_radius * 2.5
    if state.cameraDistance < 5.0:
        state.cameraDistance = 5.0

    state.cameraX = state.targetX + state.cameraDistance * math.sin(state.cameraYaw) * math.cos(state.cameraPitch)
    state.cameraY = state.targetY + state.cameraDistance * math.sin(state.cameraPitch)
    state.cameraZ = state.targetZ + state.cameraDistance * math.cos(state.cameraYaw) * math.cos(state.cameraPitch)

    texture_file = sys.argv[2] if len(sys.argv) == 3 else "resources/texture_cat.bmp"
    try :
        loaders.loadBMP(texture_file)
    except Exception as e:
        print(f"Error loading texture: {e}")

    printControls()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        width, height = glfw.get_framebuffer_size(window)
        ratio = width / float(height if height > 0 else 1)

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        math_utils.set_perspective(45.0, ratio, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        math_utils.set_look_at((state.cameraX, state.cameraY, state.cameraZ), (state.targetX, state.targetY, state.targetZ), (0.0, 1.0, 0.0))

        render.render()
        glfw.swap_buffers(window)
    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
