# src/math_utils.py
import numpy as np

def perspective_matrix(fovy_deg, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fovy_deg) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[3, 2] = (2.0 * far * near) / (near - far)
    m[2, 3] = -1.0
    return m

def ortho_matrix(left, right, bottom, top, near, far):
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = 2.0 / (right - left)
    m[1, 1] = 2.0 / (top - bottom)
    m[2, 2] = -2.0 / (far - near)
    m[3, 0] = -(right + left) / (right - left)
    m[3, 1] = -(top + bottom) / (top - bottom)
    m[3, 2] = -(far + near) / (far - near)
    return m

def look_at(position, target, up):
    zaxis =_normalize(position - target)
    xaxis = _normalize(np.cross(up, zaxis))
    yaxis = np.cross(zaxis, xaxis)

    view_matrix = np.identity(4, dtype=np.float32)
    view_matrix[0, 0:3] = xaxis
    view_matrix[1, 0:3] = yaxis
    view_matrix[2, 0:3] = zaxis
    
    trans_matrix = np.identity(4, dtype=np.float32)
    trans_matrix[3, 0:3] = -position

    return trans_matrix @ view_matrix.T # Transpose is crucial here

def _normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm