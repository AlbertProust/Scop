"""File loaders for OBJ models and BMP textures."""
from OpenGL.GL import *
import config


def loadBMP(filename):
    """
    Load a BMP (Bitmap) image file without external libraries.
    Supports uncompressed 24-bit and 32-bit BMP files.
    """
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
                    
                    pixel_data[dst_idx] = row[src_idx + 2]      # R
                    pixel_data[dst_idx + 1] = row[src_idx + 1]  # G
                    pixel_data[dst_idx + 2] = row[src_idx]      # B
            
            config.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, config.texture_id)
            
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


def loadOBJ(filename):
    """Load an OBJ model file and populate global vertex/face data."""
    try:
        x, y, z = [], [], []
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.strip().split()[1:]
                    xa, ya, za = map(float, parts)
                    config.vertices.append((xa, ya, za))
                    x.append(xa); y.append(ya); z.append(za)
                elif line.startswith("f "):
                    parts = line.strip().split()[1:]
                    face = [int(p.split("/")[0]) - 1 for p in parts]
                    # Triangulate polygons with more than 3 vertices
                    if len(face) >= 3:
                        
                        shade = 0.2 + 0.6 * ((len(config.colors) % 10) / 9.0)
                        color = (shade, shade, shade)
                        for i in range(1, len(face) - 1):
                            polygon = [face[0], face[i], face[i + 1]]
                            config.faces.append(polygon)
                            config.colors.append(color)
        
        config.targetX = (max(x) + min(x))/2
        config.targetY = (max(y) + min(y))/2
        config.targetZ = (max(z) + min(z))/2
        range_x = max(x) - min(x)
        range_z = max(z) - min(z)

        # eviter division par 0
        if range_x == 0: range_x = 1.0
        if range_z == 0: range_z = 1.0

        for (x2, y2, z2) in config.vertices:
            u = (x2 - min(x)) / range_x
            v = (z2 - min(z)) / range_z
            config.texture_coords.append((u, v))
        return True
    except Exception as e:
        print(f"Erreur chargement OBJ : {e}")
        return False
