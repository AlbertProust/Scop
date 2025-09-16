import sys
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# ===============================
# Variables caméra
# ===============================
cameraX, cameraY, cameraZ = 0.0, 0.0, 5.0
targetX, targetY, targetZ = 0.0, 0.0, 0.0
cameraDistance = 5.0
cameraYaw = 0.0
cameraPitch = 0.0

# ===============================
# Stockage du modèle
# ===============================
vertices = []
indices = []


# ===============================
# Callback clavier
# ===============================
def key_callback(window, key, scancode, action, mods):
    global cameraX, cameraY, cameraZ
    global targetX, targetY, targetZ
    global cameraDistance, cameraYaw, cameraPitch

    moveSpeed = 0.1
    rotateSpeed = 0.05

    if action in (glfw.PRESS, glfw.REPEAT):

        # Rotation caméra
        if key in (glfw.KEY_A, glfw.KEY_LEFT):
            cameraYaw += rotateSpeed
        if key in (glfw.KEY_D, glfw.KEY_RIGHT):
            cameraYaw -= rotateSpeed
        if key in (glfw.KEY_W, glfw.KEY_UP):
            cameraPitch += rotateSpeed
        if key in (glfw.KEY_S, glfw.KEY_DOWN):
            cameraPitch -= rotateSpeed

        # Limiter le pitch
        if cameraPitch > 1.5:
            cameraPitch = 1.5
        if cameraPitch < -1.5:
            cameraPitch = -1.5

        # Zoom
        if key == glfw.KEY_Q:
            cameraDistance += moveSpeed
        if key == glfw.KEY_E:
            cameraDistance -= moveSpeed
        if cameraDistance < 1.0:
            cameraDistance = 1.0

        # Déplacement du centre
        if key == glfw.KEY_J:
            targetX -= moveSpeed
        if key == glfw.KEY_L:
            targetX += moveSpeed
        if key == glfw.KEY_I:
            targetY += moveSpeed
        if key == glfw.KEY_K:
            targetY -= moveSpeed

        # Calcul position caméra (coord. sphériques)
        cameraX = targetX + cameraDistance * math.sin(cameraYaw) * math.cos(cameraPitch)
        cameraY = targetY + cameraDistance * math.sin(cameraPitch)
        cameraZ = targetZ + cameraDistance * math.cos(cameraYaw) * math.cos(cameraPitch)

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


# ===============================
# Chargement fichier OBJ
# ===============================
def loadOBJ(filename):
    global vertices, indices
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.strip().split()[1:]
                    x, y, z = map(float, parts)
                    vertices.append((x, y, z))
                elif line.startswith("f "):
                    parts = line.strip().split()[1:]
                    # On suppose des triangles f v1 v2 v3
                    idx = [int(p.split("/")[0]) - 1 for p in parts]
                    indices.extend(idx)
        print(f"Chargement : {len(vertices)} sommets, {len(indices)//3} faces")
        return True
    except Exception as e:
        print(f"Erreur chargement OBJ : {e}")
        return False


# ===============================
# Rendu
# ===============================
def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0, 1.0, 1.0)

    glBegin(GL_TRIANGLES)
    for i in indices:
        v = vertices[i]
        glVertex3f(*v)
    glEnd()


# ===============================
# Instructions
# ===============================
def printControls():
    print("Contrôles caméra :")
    print("  Rotation : W/S/A/D ou flèches")
    print("  Zoom     : Q (recule) / E (avance)")
    print("  Déplacer centre : I/K/J/L")
    print("  Quitter  : ESC")


# ===============================
# Main
# ===============================
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

    # Init caméra
    cameraDistance = 5.0
    cameraYaw = 0.0
    cameraPitch = 0.0
    cameraX = targetX + cameraDistance * math.sin(cameraYaw) * math.cos(cameraPitch)
    cameraY = targetY + cameraDistance * math.sin(cameraPitch)
    cameraZ = targetZ + cameraDistance * math.cos(cameraYaw) * math.cos(cameraPitch)

    if not loadOBJ(sys.argv[1]):
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
