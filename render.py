from OpenGL.GL import *
import time
import state
import glfw


def render():
    if state.transition_active:
        elapsed = time.time() - state.transition_start
        state.transition_value = min(1.0, elapsed / state.transition_duration)
        if state.transition_value >= 1.0:
            state.transition_active = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    if state.texture_used and state.texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, state.texture_id)
    else:
        glDisable(GL_TEXTURE_2D)

    glBegin(GL_TRIANGLES)
    for face, color, uv_indices in zip(state.faces, state.colors, state.face_texcoords):
        for idx, uv in zip(face, uv_indices):
            if state.texture_used and uv is not None:
                u, v = uv
                glTexCoord2f(u, v)

            if state.texture_used:
                glColor4f(1.0, 1.0, 1.0, state.transition_value)
            elif state.transition_active:
                glColor4f(color[0], color[1], color[2], state.transition_value)
            else:
                glColor3f(*color)
            x, y, z = state.vertices[idx]
            glVertex3f(x, y, z)
    glEnd()

    glDisable(GL_BLEND)