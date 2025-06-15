# src/asset_loader.py
from OpenGL.GL import *
import numpy as np
import pygame
from mesh import Mesh

class Shader:
    """A wrapper class for an OpenGL shader program."""
    def __init__(self, vert_path, frag_path):
        self.program_id = self._create_shader_program(vert_path, frag_path)

    def _compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            info_log = glGetShaderInfoLog(shader).decode()
            shader_name = "Vertex" if shader_type == GL_VERTEX_SHADER else "Fragment"
            raise Exception(f"{shader_name} shader compilation failed:\n{info_log}")
        return shader

    def _create_shader_program(self, vert_path, frag_path):
        try:
            with open(vert_path, 'r') as f: vert_src = f.read()
            with open(frag_path, 'r') as f: frag_src = f.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Shader file not found: {e.filename}")

        vert_shader = self._compile_shader(vert_src, GL_VERTEX_SHADER)
        frag_shader = self._compile_shader(frag_src, GL_FRAGMENT_SHADER)

        program = glCreateProgram()
        glAttachShader(program, vert_shader)
        glAttachShader(program, frag_shader)
        glLinkProgram(program)

        if not glGetProgramiv(program, GL_LINK_STATUS):
            info_log = glGetProgramInfoLog(program).decode()
            raise Exception(f"Shader linking failed:\n{info_log}")

        glDeleteShader(vert_shader)
        glDeleteShader(frag_shader)
        return program

    def use(self): glUseProgram(self.program_id)
    def set_mat4(self, name, mat): glUniformMatrix4fv(glGetUniformLocation(self.program_id, name), 1, GL_FALSE, mat)
    def set_vec3(self, name, vec): glUniform3fv(glGetUniformLocation(self.program_id, name), 1, vec)
    def set_int(self, name, val): glUniform1i(glGetUniformLocation(self.program_id, name), val)
    def set_bool(self, name, val): glUniform1i(glGetUniformLocation(self.program_id, name), int(val))
    def set_float(self, name, val): glUniform1f(glGetUniformLocation(self.program_id, name), val)
    def cleanup(self): glDeleteProgram(self.program_id)


def generate_cube_mesh():
    """Generates a cube mesh with corrected CCW winding order."""
    v = [
        # Positions           # Normals           # UVs
        # Back face (CCW)
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.0, 0.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 1.0, 1.0,
         0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 1.0, 0.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 1.0, 1.0,
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.0, 0.0,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 0.0, 1.0,
        # Front face (CCW)
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.0, 0.0,
         0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 1.0, 0.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 1.0, 1.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.0, 0.0,
        # Left face (CCW)
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, 1.0, 0.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, 0.0, 1.0,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0, 1.0, 1.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, 1.0, 0.0,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0, 0.0, 0.0,
        # Right face (CCW)
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0, 1.0, 0.0,
         0.5,  0.5, -0.5,  1.0,  0.0,  0.0, 1.0, 1.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0, 0.0, 1.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0, 0.0, 1.0,
         0.5, -0.5,  0.5,  1.0,  0.0,  0.0, 0.0, 0.0,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0, 1.0, 0.0,
        # Bottom face (CCW)
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.0, 1.0,
         0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 1.0, 1.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 1.0, 0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 1.0, 0.0,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 0.0, 0.0,
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.0, 1.0,
        # Top face (CCW)
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.0, 1.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 1.0, 0.0,
         0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 1.0, 1.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 1.0, 0.0,
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 0.0, 0.0
    ]
    return Mesh(v)

def load_cubemap(faces):
    """Loads 6 images into a cubemap texture."""
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
    
    for i, face_path in enumerate(faces):
        try:
            surface = pygame.image.load(face_path)
            data = pygame.image.tostring(surface, 'RGB', False) 
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, surface.get_width(), surface.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        except Exception as e:
            print(f"Failed to load cubemap face {face_path}: {e}")
            glDeleteTextures(1, [texture_id])
            return None

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    return texture_id