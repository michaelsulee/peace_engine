# src/texture_loader.py
from OpenGL.GL import *
from PIL import Image
import numpy as np
import pygame
import math
from pyrr import Vector3

def generate_procedural_normal_map(width: int, height: int, frequency: float) -> int:
    """
    Generates a procedural wavy normal map.
    """
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    image_data = np.zeros((width, height, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            # Use sine waves to create a bumpy/wavy pattern
            nx = math.cos(j * frequency) * 0.5 + 0.5
            ny = math.sin(i * frequency) * 0.5 + 0.5
            # The Z component of a normal map should be strong to point "out"
            nz = 1.0

            # Normalize the vector and map to [0, 255] color range
            normal = Vector3([nx, ny, nz]).normalized
            image_data[i, j] = [
                int((normal.x * 0.5 + 0.5) * 255),
                int((normal.y * 0.5 + 0.5) * 255),
                int((normal.z * 0.5 + 0.5) * 255),
            ]
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
    print("Generated procedural normal map.")
    return texture_id

def create_texture_from_surface(surface: pygame.Surface) -> tuple[int, int, int]:
    """
    Creates an OpenGL texture from a Pygame surface.
    """
    texture_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_width(), surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id, width, height

def generate_checkerboard_texture(width: int, height: int, c1: tuple, c2: tuple) -> int:
    """
    Generates a 2D checkerboard texture.
    """
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    image_data = np.zeros((width, height, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            if (i // 4 + j // 4) % 2 == 0:
                image_data[i, j] = c1
            else:
                image_data[i, j] = c2
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
    glBindTexture(GL_TEXTURE_2D, 0)
    print("Generated procedural checkerboard texture.")
    return texture_id

def generate_matte_texture(color: tuple[int, int, int]) -> int:
    """
    Generates a 1x1 2D texture of a solid color.
    """
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    pixel_data = np.array(color, dtype=np.uint8)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, pixel_data)
    glBindTexture(GL_TEXTURE_2D, 0)
    print(f"Generated matte texture with color {color}.")
    return texture_id

def load_cubemap(face_paths: list[str]) -> int:
    """
    Loads a cubemap texture from 6 individual face images.
    """
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
    
    for i, path in enumerate(face_paths):
        try:
            with Image.open(path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img_data = img.tobytes()
                
                glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB,
                             img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Skybox texture file not found: {path}")

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
    print("Cubemap texture loaded successfully.")
    return texture_id