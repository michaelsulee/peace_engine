# src/camera.py
import pygame
import numpy as np
import math_utils

class Camera:
    def __init__(self, position=(0, 2, 5), fov=45, aspect=1280/720, near=0.1, far=500.0):
        # Starts at (0,2,5), looking towards the origin where the cube is.
        self.position = np.array(position, dtype=np.float32)
        self.front = np.array([0, 0, -1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.world_up = np.array([0, 1, 0], dtype=np.float32)

        self.yaw = -90.0
        self.pitch = 0.0

        self.move_speed = 5.0
        self.mouse_sensitivity = 0.1

        self.update_vectors()

    def get_view_matrix(self):
        return math_utils.look_at(self.position, self.position + self.front, self.up)
    
    def update_vectors(self):
        front = np.zeros(3, dtype=np.float32)
        front[0] = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        front[1] = np.sin(np.radians(self.pitch))
        front[2] = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.front = math_utils._normalize(front)
        self.right = math_utils._normalize(np.cross(self.front, self.world_up))
        self.up = math_utils._normalize(np.cross(self.right, self.front))

    def process_keyboard(self, dt):
        keys = pygame.key.get_pressed()
        velocity = self.move_speed * dt
        if keys[pygame.K_w]: self.position += self.front * velocity
        if keys[pygame.K_s]: self.position -= self.front * velocity
        if keys[pygame.K_a]: self.position -= self.right * velocity
        if keys[pygame.K_d]: self.position += self.right * velocity
        if keys[pygame.K_SPACE]: self.position += self.world_up * velocity
        if keys[pygame.K_LSHIFT]: self.position -= self.world_up * velocity

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        self.yaw += x_offset * self.mouse_sensitivity
        self.pitch -= y_offset * self.mouse_sensitivity

        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))
        
        self.update_vectors()