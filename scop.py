import sys
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import math
import random

cameraX, cameraY, cameraZ = 0.0, 0.0, 5.0
targetX, targetY, targetZ = 0.0, 0.0, 0.0
cameraDistance = 5.0
cameraYaw = 0.0
cameraPitch = 0.0
texture_id = None
texture_used = False
texture_coords = []
vertices, indices, faces, colors, = [], [], [], []


def key_callback(window, key, scancode, action, mods):
    global cameraX, cameraY, cameraZ
    global targetX, targetY, targetZ
    global cameraDistance, cameraYaw, cameraPitch
    global x, y, z
    global texture_used
    moveSpeed = 0.1
    rotateSpeed = 0.05

    if action in (glfw.PRESS, glfw.REPEAT):
        if key in (glfw.KEY_A, glfw.KEY_LEFT):
            cameraYaw += rotateSpeed
        if key in (glfw.KEY_D, glfw.KEY_RIGHT):
            cameraYaw -= rotateSpeed
        if key in (glfw.KEY_W, glfw.KEY_UP):
            cameraPitch += rotateSpeed
        if key in (glfw.KEY_S, glfw.KEY_DOWN):
            cameraPitch -= rotateSpeed

        if cameraPitch > 1.5:
            cameraPitch = 1.5
        if cameraPitch < -1.5:
            cameraPitch = -1.5
        if key == glfw.KEY_Q:
            cameraDistance += moveSpeed
        if key == glfw.KEY_E:
            cameraDistance -= moveSpeed
        if key == glfw.KEY_T:
            texture_used = not texture_used
        if cameraDistance < 1.0:
            cameraDistance = 1.0

        if key == glfw.KEY_J:
            targetX += moveSpeed
        if key == glfw.KEY_L:
            targetX -= moveSpeed
        if key == glfw.KEY_I:
            targetY += moveSpeed
        if key == glfw.KEY_K:
            targetY -= moveSpeed

        
        # print(((min.x, max.x), sum((min.x, max.x)), (targetX, targetY, targetZ)))
        # print( (max(x) + min(x))/2, (max(y) + min(y))/2, (max(z) + min(z))/2)
        cameraX = targetX + cameraDistance * math.sin(cameraYaw) * math.cos(cameraPitch)
        cameraY = targetY + cameraDistance * math.sin(cameraPitch)
        cameraZ = targetZ + cameraDistance * math.cos(cameraYaw) * math.cos(cameraPitch)

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def loadOBJ(filename):
    global vertices, indices
    global targetX, targetY, targetZ
    global texture_coords
    try:
        x, y, z = [], [], []
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.strip().split()[1:]
                    xa, ya, za = map(float, parts)
                    vertices.append((xa, ya, za))
                    x.append(xa); y.append(ya); z.append(za)
                elif line.startswith("f "):
                    parts = line.strip().split()[1:]
                    face = [int(p.split("/")[0]) - 1 for p in parts]
                    if len(face) == 3:
                        faces.append(face)
                        colors.append((random.random(), random.random(), random.random()))
        targetX = (max(x) + min(x))/2
        targetY = (max(y) + min(y))/2
        targetZ = (max(z) + min(z))/2
        range_x = max(x) - min(x)
        range_z = max(z) - min(z)

        # eviter division par 0
        if range_x == 0: range_x = 1.0
        if range_z == 0: range_z = 1.0

        for (x2, y2, z2) in vertices:
            u = (x2 - min(x)) / range_x
            v = (z2 - min(z)) / range_z
            texture_coords.append((u, v))
        return True
    except Exception as e:
        print(f"Erreur chargement OBJ : {e}")
        return False

def loadTEXTURE(filename):

    global texture_id
    try:
        img = Image.open(filename).transpose(Image.FLIP_TOP_BOTTOM)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        if img.mode == "RGB":
            fmt = GL_RGB
        else:
            fmt = GL_RGBA
            img = img.convert("RGBA")

        img_data = img.tobytes()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexImage2D(GL_TEXTURE_2D, 0, fmt, img.width, img.height, 0, fmt,
                      GL_UNSIGNED_BYTE, img_data)

        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        print("Texture loaded", "mode:", img.mode)
        return (True)
    except Exception as e:
        print(f"Erreur chargement Texture : {e}")
        return False

def render():

    global texture_used

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if texture_used and texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else :
        glDisable(GL_TEXTURE_2D)
    
    glBegin(GL_TRIANGLES)
    for face, color in zip(faces, colors):
        if not texture_used:
            glColor3f(*color)
        for idx in face:
            if texture_used and texture_coords:
                u, v = texture_coords[idx]
                glTexCoord2f(u, v)
            x, y, z = vertices[idx]
            glVertex3f(x, y, z)
    glEnd()
    if texture_used:
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

def printControls():
    print("Contrôles caméra :")
    print("  Rotation : W/S/A/D ou flèches")
    print("  Zoom     : Q (recule) / E (avance)")
    print("  Déplacer centre : I/K/J/L")
    print("  Quitter  : ESC")

def main():
    global cameraX, cameraY, cameraZ, cameraDistance, cameraYaw, cameraPitch

    if len(sys.argv) != 2:
        print("Usage: python viewer.py fichier.obj")
        return

    if not glfw.init():
        print("Erreur GLFW")
        return

    window = glfw.create_window(1600, 1200, "Visualiseur .OBJ en Python", None, None)
    if not window:
        glfw.terminate()
        print("Impossible de créer la fenêtre")
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)

    cameraDistance = 5.0
    cameraYaw = 0.0
    cameraPitch = 0.0
    cameraX = targetX + cameraDistance * math.sin(cameraYaw) * math.cos(cameraPitch)
    cameraY = targetY + cameraDistance * math.sin(cameraPitch)
    cameraZ = targetZ + cameraDistance * math.cos(cameraYaw) * math.cos(cameraPitch)

    if not loadOBJ(sys.argv[1]):
        glfw.terminate()
        return
    if not loadTEXTURE("resources/texture.png"):
        glfw.terminate()
        return

    printControls()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        width, height = glfw.get_framebuffer_size(window)
        ratio = width / float(height)

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, ratio, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(cameraX, cameraY, cameraZ,
                  targetX, targetY, targetZ,
                  0.0, 1.0, 0.0)

        render()
        glfw.swap_buffers(window)

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
