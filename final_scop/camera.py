import math
import glfw
import state


def key_callback(window, key, scancode, action, mods):
    moveSpeed = 0.1
    rotateSpeed = 0.05

    if action in (glfw.PRESS, glfw.REPEAT):
        if key in (glfw.KEY_A, glfw.KEY_LEFT):
            state.cameraYaw += rotateSpeed
        if key in (glfw.KEY_D, glfw.KEY_RIGHT):
            state.cameraYaw -= rotateSpeed
        if key in (glfw.KEY_W, glfw.KEY_UP):
            state.cameraPitch += rotateSpeed
        if key in (glfw.KEY_S, glfw.KEY_DOWN):
            state.cameraPitch -= rotateSpeed

        state.cameraPitch = max(-1.5, min(1.5, state.cameraPitch))

        if key == glfw.KEY_Q:
            state.cameraDistance += moveSpeed
        if key == glfw.KEY_E:
            state.cameraDistance -= moveSpeed
        if key == glfw.KEY_T and state.texture_id:
            state.texture_used = not state.texture_used
        if state.cameraDistance < 1.0:
            state.cameraDistance = 1.0

        if key == glfw.KEY_J:
            state.targetX += moveSpeed
        if key == glfw.KEY_L:
            state.targetX -= moveSpeed
        if key == glfw.KEY_I:
            state.targetY += moveSpeed
        if key == glfw.KEY_K:
            state.targetY -= moveSpeed

        state.cameraX = state.targetX + state.cameraDistance * math.sin(state.cameraYaw) * math.cos(state.cameraPitch)
        state.cameraY = state.targetY + state.cameraDistance * math.sin(state.cameraPitch)
        state.cameraZ = state.targetZ + state.cameraDistance * math.cos(state.cameraYaw) * math.cos(state.cameraPitch)

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
