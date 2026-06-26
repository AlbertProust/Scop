import sys
import glfw
from OpenGL.GL import *
import math
import os

# Minimal replacements for GLU functionality (gluPerspective, gluLookAt)
def _normalize(v):
    l = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if l == 0:
        return (0.0, 0.0, 0.0)
    return (v[0]/l, v[1]/l, v[2]/l)

def _cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def set_perspective(fovy, aspect, znear, zfar):
    """Load a perspective projection matrix (column-major)."""
    f = 1.0 / math.tan(math.radians(fovy) / 2.0)
    m = [
        f / aspect, 0.0, 0.0, 0.0,
        0.0, f, 0.0, 0.0,
        0.0, 0.0, (zfar + znear) / (znear - zfar), -1.0,
        0.0, 0.0, (2.0 * zfar * znear) / (znear - zfar), 0.0,
    ]
    glLoadMatrixf(m)

def set_look_at(eye, center, up):
    """Load a view matrix like gluLookAt. """
    f = _normalize((center[0]-eye[0], center[1]-eye[1], center[2]-eye[2]))
    s = _normalize(_cross(f, up))
    u = _cross(s, f)
    m = [
        s[0], u[0], -f[0], 0.0,
        s[1], u[1], -f[1], 0.0,
        s[2], u[2], -f[2], 0.0,
        -_dot(s, eye), -_dot(u, eye), _dot(f, eye), 1.0,
    ]
    glLoadMatrixf(m)

cameraX, cameraY, cameraZ = 0.0, 0.0, 5.0
targetX, targetY, targetZ = 0.0, 0.0, 0.0
cameraDistance = 5.0
cameraYaw = 0.0
cameraPitch = 0.0
obj_radius = 1.0
texture_id = None
texture_used = False
texture_coords = []
face_texcoords = []
vertices, indices, faces, colors, = [], [], [], []


def loadBMP(filename):
    """
    Load a BMP (Bitmap) image file without external libraries.
    Supports uncompressed 24-bit and 32-bit BMP files.
    """
    global texture_id
    try:
        with open(filename, 'rb') as f:
            # Read BMP file header (14 bytes)
            header = f.read(14)
            if header[0:2] != b'BM':
                print("Error: Not a valid BMP file")
                return False
            
            # Read DIB header (40 bytes for standard BMP)
            dib_header = f.read(40)
            
            # Parse header info (little-endian)
            width = int.from_bytes(dib_header[4:8], 'little')
            height = int.from_bytes(dib_header[8:12], 'little')
            bits_per_pixel = int.from_bytes(dib_header[14:16], 'little')
            compression = int.from_bytes(dib_header[16:20], 'little')
            
            if compression != 0:
                print("Error: Compressed BMP files not supported")
                return False
            
            if bits_per_pixel not in [24, 32]:
                print(f"Error: Only 24-bit and 32-bit BMP supported (found {bits_per_pixel}-bit)")
                return False
            
            # Read pixel data
            bytes_per_pixel = bits_per_pixel // 8
            row_size = (width * bytes_per_pixel + 3) // 4 * 4  # Rows are padded to 4-byte boundary
            
            # BMP stores image bottom-to-top, we need to flip it
            pixel_data = bytearray(width * height * 3)
            
            for y in range(height):
                row = f.read(row_size)
                if len(row) < width * bytes_per_pixel:
                    print("Error: Incomplete pixel data")
                    return False
                
                # Flip vertically and convert BGR to RGB
                dest_y = height - 1 - y
                for x in range(width):
                    src_idx = x * bytes_per_pixel
                    dst_idx = (dest_y * width + x) * 3
                    
                    # BMP uses BGR order, convert to RGB
                    pixel_data[dst_idx] = row[src_idx + 2]      # R
                    pixel_data[dst_idx + 1] = row[src_idx + 1]  # G
                    pixel_data[dst_idx + 2] = row[src_idx]      # B
            
            # Create OpenGL texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0,
                         GL_RGB, GL_UNSIGNED_BYTE, bytes(pixel_data))
            
            glBindTexture(GL_TEXTURE_2D, 0)
            print(f"BMP texture loaded: {filename} ({width}x{height}, {bits_per_pixel}-bit)")
            return True
            
    except Exception as e:
        print(f"Error loading BMP: {e}")
        return False


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
        if key == glfw.KEY_T and texture_id:
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

        
        cameraX = targetX + cameraDistance * math.sin(cameraYaw) * math.cos(cameraPitch)
        cameraY = targetY + cameraDistance * math.sin(cameraPitch)
        cameraZ = targetZ + cameraDistance * math.cos(cameraYaw) * math.cos(cameraPitch)

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def loadOBJ(filename):
    global vertices, indices
    global targetX, targetY, targetZ
    global texture_coords, face_texcoords
    try:
        x, y, z = [], [], []
        texcoords = []
        face_uvs = []
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.strip().split()[1:]
                    xa, ya, za = map(float, parts)
                    vertices.append((xa, ya, za))
                    x.append(xa); y.append(ya); z.append(za)
                elif line.startswith("vt "):
                    parts = line.strip().split()[1:]
                    u, v = map(float, parts[:2])
                    texcoords.append((u, 1.0 - v))
                elif line.startswith("f "):
                    parts = line.strip().split()[1:]
                    face = []
                    face_uv = []
                    for p in parts:
                        vals = p.split("/")
                        vidx = int(vals[0]) - 1
                        face.append(vidx)
                        if len(vals) > 1 and vals[1] != "":
                            uv_idx = int(vals[1]) - 1
                            face_uv.append(texcoords[uv_idx])
                        else:
                            face_uv.append(None)
                    if len(face) >= 3:
                        shade = 0.2 + 0.6 * ((len(colors) % 10) / 9.0)
                        color = (shade, shade, shade)
                        for i in range(1, len(face) - 1):
                            polygon = [face[0], face[i], face[i + 1]]
                            polygon_uv = [face_uv[0], face_uv[i], face_uv[i + 1]]
                            faces.append(polygon)
                            face_texcoords.append(polygon_uv)
                            colors.append(color)
        targetX = (max(x) + min(x))/2
        targetY = (max(y) + min(y))/2
        targetZ = (max(z) + min(z))/2
        dx = max(x) - min(x)
        dy = max(y) - min(y)
        dz = max(z) - min(z)
        obj_radius = math.sqrt(dx*dx + dy*dy + dz*dz) * 0.5
        globals()['obj_radius'] = obj_radius if obj_radius > 0.0 else 1.0
        if not texcoords:
            range_x = dx
            range_y = dy
            range_z = dz
            if range_x == 0: range_x = 1.0
            if range_y == 0: range_y = 1.0
            if range_z == 0: range_z = 1.0
            for (x2, y2, z2) in vertices:
                texture_coords.append(((x2 - min(x)) / range_x, (z2 - min(z)) / range_z))
            face_texcoords = [[texture_coords[idx] for idx in face] for face in faces]
        else:
            # Keep face-specific UVs when OBJ provides vt coordinates.
            pass
        return True
    except Exception as e:
        print(f"Erreur chargement OBJ : {e}")
        return False


def render():

    global texture_used
    global vertices
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if texture_used and texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else :
        glDisable(GL_TEXTURE_2D)
    
    glBegin(GL_TRIANGLES)
    for face, color, uv_indices in zip(faces, colors, face_texcoords):
        if not texture_used:
            glColor3f(*color)
        for idx, uv in zip(face, uv_indices):
            if texture_used and uv is not None:
                u, v = uv
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
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Usage: python viewer.py fichier.obj optional_texture.obj")
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
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)

    filename, file_extension = os.path.splitext(sys.argv[1])
    if file_extension.lower() != ".obj":
        print("Error: The first argument must be an .obj file")
        glfw.terminate()
        return

    if not loadOBJ(sys.argv[1]):
        glfw.terminate()
        return
        
    cameraYaw = 0.0
    cameraPitch = 0.0
    cameraDistance = obj_radius * 2.5
    if cameraDistance < 5.0:
        cameraDistance = 5.0

    cameraX = targetX + cameraDistance * math.sin(cameraYaw) * math.cos(cameraPitch)
    cameraY = targetY + cameraDistance * math.sin(cameraPitch)
    cameraZ = targetZ + cameraDistance * math.cos(cameraYaw) * math.cos(cameraPitch)

    loadBMP(sys.argv[2] if len(sys.argv) == 3 else "resources/texture_cat.bmp")
        
    printControls()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        width, height = glfw.get_framebuffer_size(window)
        ratio = width / float(height if height > 0 else 1)

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        set_perspective(45.0, ratio, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        set_look_at((cameraX, cameraY, cameraZ), (targetX, targetY, targetZ), (0.0, 1.0, 0.0))
        render()
        glfw.swap_buffers(window)

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main() 