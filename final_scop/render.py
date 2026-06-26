from OpenGL.GL import *
import state


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if state.texture_used and state.texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, state.texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glDisable(GL_TEXTURE_2D)

    glBegin(GL_TRIANGLES)
    for face, color, uv_indices in zip(state.faces, state.colors, state.face_texcoords):
        if not state.texture_used:
            glColor3f(*color)
        for idx, uv in zip(face, uv_indices):
            if state.texture_used and uv is not None:
                u, v = uv
                glTexCoord2f(u, v)
            x, y, z = state.vertices[idx]
            glVertex3f(x, y, z)
    glEnd()

    if state.texture_used:
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
