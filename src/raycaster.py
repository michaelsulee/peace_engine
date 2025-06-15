# src/raycaster.py
import numpy as np

class Raycaster:
    """Handles raycasting for selection and object placement."""
    def __init__(self, camera, projection_matrix):
        self.camera = camera
        self.proj_matrix = projection_matrix
        self.view_matrix = None # Updated each frame by the engine
        self.inv_proj_matrix = np.linalg.inv(self.proj_matrix)
        self.inv_view_matrix = np.identity(4) # Initial placeholder

    def update_matrices(self, view_matrix):
        """
        Updates the view matrix and its inverse once per frame.
        This is more efficient than recalculating it for every ray.
        """
        self.view_matrix = view_matrix
        self.inv_view_matrix = np.linalg.inv(self.view_matrix)

    def get_ray_from_mouse(self, mouse_x, mouse_y, screen_width, screen_height):
        """Converts 2D mouse coordinates to a 3D world space ray direction vector."""
        # 1. To Normalized Device Coordinates (NDC): [-1, 1] range
        ndc_x = (2.0 * mouse_x) / screen_width - 1.0
        ndc_y = 1.0 - (2.0 * mouse_y) / screen_height
        
        # 2. To Homogeneous Clip Space: The z=-1 points to the front of the clip space
        ray_clip = np.array([ndc_x, ndc_y, -1.0, 1.0], dtype=np.float32)

        # 3. To Eye/View Space: Un-project by multiplying with inverse projection matrix
        ray_eye = self.inv_proj_matrix @ ray_clip
        ray_eye = np.array([ray_eye[0], ray_eye[1], -1.0, 0.0]) # Set z to forward, w to 0 for a direction

        # 4. To World Space: Un-transform by multiplying with inverse view matrix
        ray_world_vec = (self.inv_view_matrix @ ray_eye)[:3]
        return np.linalg.norm(ray_world_vec)

    def get_ray_from_center(self):
        """A simplified raycast directly from the camera's front vector."""
        return self.camera.front

    def intersect_ray_aabb(self, ray_origin, ray_dir, aabb_min, aabb_max):
        """Checks for intersection between a ray and an AABB (Slab test)."""
        t_min = 0.0
        t_max = float('inf')

        for i in range(3):
            if abs(ray_dir[i]) < 1e-6: # Ray is parallel to the slab
                if ray_origin[i] < aabb_min[i] or ray_origin[i] > aabb_max[i]:
                    return False # Parallel and outside
            else:
                t1 = (aabb_min[i] - ray_origin[i]) / ray_dir[i]
                t2 = (aabb_max[i] - ray_origin[i]) / ray_dir[i]

                if t1 > t2: t1, t2 = t2, t1 # Ensure t1 is the smaller intersection time

                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
        
        return t_min <= t_max
    
    def intersect_ray_plane(self, ray_origin, ray_dir, plane_normal=np.array([0,1,0]), plane_point=np.array([0,0,0])):
        """Finds the intersection point of a ray and an infinite plane."""
        denom = np.dot(plane_normal, ray_dir)
        if abs(denom) > 1e-6: # Ensure ray is not parallel to the plane
            p0l0 = plane_point - ray_origin
            t = np.dot(p0l0, plane_normal) / denom
            if t >= 0: # Intersection is in the positive direction of the ray
                return ray_origin + t * ray_dir
        return None