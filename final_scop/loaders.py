import math
from OpenGL.GL import *
import state


def loadBMP(filename):
    """Load a BMP image file and create an OpenGL texture."""
    try:
        with open(filename, 'rb') as f:
            header = f.read(14)
            if header[0:2] != b'BM':
                print("Error: Not a valid BMP file")
                return False

            dib_header = f.read(40)
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

            bytes_per_pixel = bits_per_pixel // 8
            row_size = (width * bytes_per_pixel + 3) // 4 * 4
            pixel_data = bytearray(width * height * 3)

            for y in range(height):
                row = f.read(row_size)
                if len(row) < width * bytes_per_pixel:
                    print("Error: Incomplete pixel data")
                    return False
                dest_y = height - 1 - y
                for x in range(width):
                    src_idx = x * bytes_per_pixel
                    dst_idx = (dest_y * width + x) * 3
                    pixel_data[dst_idx] = row[src_idx + 2]
                    pixel_data[dst_idx + 1] = row[src_idx + 1]
                    pixel_data[dst_idx + 2] = row[src_idx]

            state.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, state.texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(pixel_data))
            glBindTexture(GL_TEXTURE_2D, 0)
            print(f"BMP texture loaded: {filename} ({width}x{height}, {bits_per_pixel}-bit)")
            return True
    except Exception as e:
        print(f"Error loading BMP: {e}")
        return False


def loadOBJ(filename):
    """Load a wavefront OBJ and build vertex/UV/face arrays."""
    state.vertices = []
    state.faces = []
    state.colors = []
    state.texture_coords = []
    state.face_texcoords = []
    state.indices = []

    try:
        x, y, z = [], [], []
        texcoords = []

        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    parts = line.strip().split()[1:]
                    xa, ya, za = map(float, parts)
                    state.vertices.append((xa, ya, za))
                    x.append(xa); y.append(ya); z.append(za)
                elif line.startswith('vt '):
                    parts = line.strip().split()[1:]
                    u, v = map(float, parts[:2])
                    texcoords.append((u, 1.0 - v))
                elif line.startswith('f '):
                    parts = line.strip().split()[1:]
                    face = []
                    face_uv = []
                    for p in parts:
                        vals = p.split('/')
                        vidx = int(vals[0]) - 1
                        face.append(vidx)
                        if len(vals) > 1 and vals[1] != '':
                            uv_idx = int(vals[1]) - 1
                            face_uv.append(texcoords[uv_idx])
                        else:
                            face_uv.append(None)
                    if len(face) >= 3:
                        shade = 0.2 + 0.6 * ((len(state.colors) % 10) / 9.0)
                        color = (shade, shade, shade)
                        for i in range(1, len(face) - 1):
                            polygon = [face[0], face[i], face[i + 1]]
                            polygon_uv = [face_uv[0], face_uv[i], face_uv[i + 1]]
                            state.faces.append(polygon)
                            state.face_texcoords.append(polygon_uv)
                            state.colors.append(color)

        state.targetX = (max(x) + min(x)) / 2
        state.targetY = (max(y) + min(y)) / 2
        state.targetZ = (max(z) + min(z)) / 2

        dx = max(x) - min(x)
        dy = max(y) - min(y)
        dz = max(z) - min(z)
        obj_radius = math.sqrt(dx*dx + dy*dy + dz*dz) * 0.5
        state.obj_radius = obj_radius if obj_radius > 0.0 else 1.0

        if not texcoords:
            range_x = dx if dx != 0 else 1.0
            range_y = dy if dy != 0 else 1.0
            range_z = dz if dz != 0 else 1.0
            for (x2, y2, z2) in state.vertices:
                state.texture_coords.append(((x2 - min(x)) / range_x, (z2 - min(z)) / range_z))
            state.face_texcoords = [[state.texture_coords[idx] for idx in face] for face in state.faces]

        return True
    except Exception as e:
        print(f"Erreur chargement OBJ : {e}")
        return False
