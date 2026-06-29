import math
from OpenGL.GL import glLoadMatrixf


def _normalize(v):
    l = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if l == 0:
        return (0.0, 0.0, 0.0)
    return (v[0]/l, v[1]/l, v[2]/l)


def _cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )


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
    """Load a view matrix like gluLookAt."""
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
