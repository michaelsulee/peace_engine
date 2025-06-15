# src/camera.py
from pyrr import Vector3, Matrix44, vector, vector3, matrix44
import math

class Camera:
    def __init__(self, position: Vector3, aspect_ratio: float):
        self.position = position
        self.front = Vector3([0.0, 0.0, -1.0])
        self.up = Vector3([0.0, 1.0, 0.0])
        self.world_up = Vector3([0.0, 1.0, 0.0])
        self.right = vector.normalise(vector3.cross(self.front, self.world_up))
        self.yaw = -90.0
        self.pitch = 0.0
        self.movement_speed = 5.0
        self.mouse_sensitivity = 0.1
        self.fov = 45.0
        self.near_plane = 0.1
        self.far_plane = 1000.0 # Increased far plane for larger scene
        self.aspect_ratio = aspect_ratio
        self.update_camera_vectors()
    def get_view_matrix(self) -> Matrix44:
        return matrix44.create_look_at(self.position, self.position + self.front, self.up)
    def get_projection_matrix(self) -> Matrix44:
        return matrix44.create_perspective_projection(self.fov, self.aspect_ratio, self.near_plane, self.far_plane)
    def process_keyboard(self, direction: str, delta_time: float):
        velocity = self.movement_speed * delta_time
        if direction == "FORWARD": self.position += self.front * velocity
        if direction == "BACKWARD": self.position -= self.front * velocity
        if direction == "LEFT": self.position -= self.right * velocity
        if direction == "RIGHT": self.position += self.right * velocity
        if direction == "UP": self.position += self.world_up * velocity
        if direction == "DOWN": self.position -= self.world_up * velocity
    def process_mouse_movement(self, x_offset: float, y_offset: float, constrain_pitch: bool = True):
        self.yaw += x_offset * self.mouse_sensitivity
        self.pitch += y_offset * self.mouse_sensitivity
        if constrain_pitch: self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update_camera_vectors()
    def update_camera_vectors(self):
        new_front = Vector3([0.0, 0.0, 0.0])
        new_front.x = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        new_front.y = math.sin(math.radians(self.pitch))
        new_front.z = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = vector.normalise(new_front)
        self.right = vector.normalise(vector3.cross(self.front, self.world_up))
        self.up = vector.normalise(vector3.cross(self.right, self.front))