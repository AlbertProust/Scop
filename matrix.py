"""Matrix and vector operations for 3D graphics."""
import math


def vec_sub(a, b):
    """Subtract two 3D vectors."""
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def vec_cross(a, b):
    """Cross product of two 3D vectors."""
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]


def vec_dot(a, b):
    """Dot product of two 3D vectors."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec_normalize(v):
    """Normalize a 3D vector."""
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length == 0:
        return v
    return [v[0] / length, v[1] / length, v[2] / length]


def perspective_matrix(fov, aspect, near, far):
    """Create a perspective projection matrix.
    
    Args:
        fov: Field of view in degrees
        aspect: Aspect ratio (width / height)
        near: Near clipping plane
        far: Far clipping plane
    
    Returns:
        4x4 perspective projection matrix as list of lists
    """
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    
    return [
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), -1.0],
        [0.0, 0.0, (2.0 * far * near) / (near - far), 0.0]
    ]


def lookAt_matrix(eye, center, up):
    """Create a lookAt view matrix.
    
    Args:
        eye: Camera position (x, y, z)
        center: Target position (x, y, z)
        up: Up vector (x, y, z)
    
    Returns:
        4x4 view matrix as list of lists
    """
    # Forward vector (from eye to center)
    f = vec_normalize(vec_sub(center, eye))
    
    # Right vector (cross product of forward and up)
    s = vec_normalize(vec_cross(f, up))
    
    # True up vector (cross product of right and forward)
    u = vec_cross(s, f)
    
    return [
        [s[0], u[0], -f[0], 0.0],
        [s[1], u[1], -f[1], 0.0],
        [s[2], u[2], -f[2], 0.0],
        [-vec_dot(s, eye), -vec_dot(u, eye), vec_dot(f, eye), 1.0]
    ]


def matrix_to_flat_list(matrix):
    """Convert a 4x4 matrix to a flattened list in column-major order (for OpenGL)."""
    result = []
    for col in range(4):
        for row in range(4):
            result.append(matrix[row][col])
    return result
