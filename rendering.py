"""3D rendering functionality."""
from OpenGL.GL import *
import config


def render():
    """Render the 3D scene."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if config.texture_used and config.texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, config.texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glDisable(GL_TEXTURE_2D)
    
    glBegin(GL_TRIANGLES)
    for face, color in zip(config.faces, config.colors):
        if not config.texture_used:
            glColor3f(*color)
        for idx in face:
            if config.texture_used and config.texture_coords:
                u, v = config.texture_coords[idx]
                glTexCoord2f(u, v)
            x, y, z = config.vertices[idx]
            glVertex3f(x, y, z)
    glEnd()
    if config.texture_used:
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
