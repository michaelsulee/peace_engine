# src/transform.py
import numpy as np
from math_utils import _normalize # <-- FIXED

class Transform:
    """Encapsulates position, rotation, and scale to compute a model matrix."""
    def __init__(self, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32) # Euler angles in radians
        self.scale_v = np.array(scale, dtype=np.float32)
        self._model_matrix = np.identity(4, dtype=np.float32)
        self.is_dirty = True # Flag to trigger matrix recalculation

    def get_model_matrix(self):
        """Calculates and returns the model matrix, only if transformations have changed."""
        if self.is_dirty:
            # T * R * S multiplication order
            trans = np.identity(4, dtype=np.float32)
            trans[3, :3] = self.position

            rot_x = self._rotation_matrix(self.rotation[0], [1, 0, 0])
            rot_y = self._rotation_matrix(self.rotation[1], [0, 1, 0])
            rot_z = self._rotation_matrix(self.rotation[2], [0, 0, 1])
            # Combine rotations: order (e.g., ZYX) is crucial for predictable results
            rot = rot_z @ rot_y @ rot_x

            scl = np.diag([*self.scale_v, 1.0]).astype(np.float32)

            self._model_matrix = scl @ rot @ trans
            self.is_dirty = False
        return self._model_matrix
    
    def _rotation_matrix(self, angle, axis):
        axis = _normalize(np.array(axis))
        c, s = np.cos(angle), np.sin(angle)
        t = 1.0 - c
        x, y, z = axis
        
        return np.array([
            [t*x*x + c,   t*x*y - z*s, t*x*z + y*s, 0],
            [t*x*y + z*s, t*y*y + c,   t*y*z - x*s, 0],
            [t*x*z - y*s, t*y*z + x*s, t*z*z + c,   0],
            [0,           0,           0,           1]
        ], dtype=np.float32)

    def set_position(self, pos):
        self.position = np.array(pos, dtype=np.float32)
        self.is_dirty = True