"""Camera controls and input handling."""
import math
import glfw
import config


def key_callback(window, key, scancode, action, mods):
    """Handle keyboard input for camera control."""
    moveSpeed = 0.1
    rotateSpeed = 0.05

    if action in (glfw.PRESS, glfw.REPEAT):
        match key:
            case glfw.KEY_A, glfw.KEY_LEFT, glfw.KEY_D, glfw.KEY_RIGHT:
                if key in (glfw.KEY_A, glfw.KEY_LEFT):
                    config.cameraYaw += rotateSpeed if rotateSpeed < 1.5 else 1.5
                else:
                    config.cameraYaw -= rotateSpeed if rotateSpeed > -1.5 else -1.5

            case glfw.KEY_W, glfw.KEY_UP, glfw.KEY_S, glfw.KEY_DOWN:
                if key in (glfw.KEY_W, glfw.KEY_UP):
                    config.cameraPitch += rotateSpeed
                else:
                    config.cameraPitch -= rotateSpeed

        if config.cameraPitch > 1.5:
            config.cameraPitch = 1.5
        if config.cameraPitch < -1.5:
            config.cameraPitch = -1.5
        
        if key == glfw.KEY_Q:
            config.cameraDistance += moveSpeed
        if key == glfw.KEY_E:
            config.cameraDistance -= moveSpeed
        if key == glfw.KEY_T and config.texture_id:
            config.texture_used = not config.texture_used
        if config.cameraDistance < 1.0:
            config.cameraDistance = 1.0

        if key == glfw.KEY_J:
            config.targetX += moveSpeed
        if key == glfw.KEY_L:
            config.targetX -= moveSpeed
        if key == glfw.KEY_I:
            config.targetY += moveSpeed
        if key == glfw.KEY_K:
            config.targetY -= moveSpeed

        
        config.cameraX = config.targetX + config.cameraDistance * math.sin(config.cameraYaw) * math.cos(config.cameraPitch)
        config.cameraY = config.targetY + config.cameraDistance * math.sin(config.cameraPitch)
        config.cameraZ = config.targetZ + config.cameraDistance * math.cos(config.cameraYaw) * math.cos(config.cameraPitch)

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def print_controls():
    """Print camera control instructions."""
    print("Contrôles caméra :")
    print("  Rotation : W/S/A/D ou flèches")
    print("  Zoom     : Q (recule) / E (avance)")
    print("  Déplacer centre : I/K/J/L")
    print("  Quitter  : ESC")
