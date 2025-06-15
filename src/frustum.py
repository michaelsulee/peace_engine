# src/frustum.py
import numpy as np

class Frustum:
    """Represents the viewing frustum for culling off-screen objects."""
    def __init__(self):
        # 6 planes, each with 4 components (A, B, C, D) for the plane equation Ax + By + Cz + D = 0
        self.planes = np.zeros((6, 4), dtype=np.float32)

    def update(self, view_proj_matrix):
        """Extracts the 6 planes from the combined view-projection matrix."""
        # The matrix is transposed for easier access to columns
        mat = view_proj_matrix.T
        
        # Left plane
        self.planes[0] = mat[3] + mat[0]
        # Right plane
        self.planes[1] = mat[3] - mat[0]
        # Bottom plane
        self.planes[2] = mat[3] + mat[1]
        # Top plane
        self.planes[3] = mat[3] - mat[1]
        # Near plane
        self.planes[4] = mat[3] + mat[2]
        # Far plane
        self.planes[5] = mat[3] - mat[2]

        # Normalize the planes
        for i in range(6):
            magnitude = np.linalg.norm(self.planes[i, :3])
            if magnitude > 0:
                self.planes[i] /= magnitude

    def is_box_in_frustum(self, aabb_min, aabb_max):
        """Checks if an Axis-Aligned Bounding Box is inside the frustum."""
        for plane in self.planes:
            # Find the corner of the AABB that is "most positive"
            # with respect to the plane normal.
            p_corner = np.array([
                aabb_max[0] if plane[0] > 0 else aabb_min[0],
                aabb_max[1] if plane[1] > 0 else aabb_min[1],
                aabb_max[2] if plane[2] > 0 else aabb_min[2]
            ])
            
            # If this corner is outside the plane, the entire box is outside.
            if np.dot(plane[:3], p_corner) + plane[3] < 0:
                return False
        return True