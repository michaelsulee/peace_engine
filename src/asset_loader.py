# src/asset_loader.py
from OpenGL.GL import *
import numpy as np
from mesh import Mesh
from pyrr import matrix44, Vector3, Vector4
import math

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program_id = self._create_shader_program(vertex_path, fragment_path)
    def _read_file(self, file_path):
        with open(file_path, 'r') as f: return f.read()
    def _compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode('utf-8')
            glDeleteShader(shader)
            raise RuntimeError(f"Shader compilation failed: {error}")
        return shader
    def _create_shader_program(self, vertex_path, fragment_path):
        v_source, f_source = self._read_file(vertex_path), self._read_file(fragment_path)
        v_shader, f_shader = self._compile_shader(v_source, GL_VERTEX_SHADER), self._compile_shader(f_source, GL_FRAGMENT_SHADER)
        program = glCreateProgram()
        glAttachShader(program, v_shader); glAttachShader(program, f_shader)
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(program).decode('utf-8')
            glDeleteProgram(program)
            raise RuntimeError(f"Shader linking failed: {error}")
        glDeleteShader(v_shader); glDeleteShader(f_shader)
        return program
    def use(self): glUseProgram(self.program_id)
    def destroy(self): glDeleteProgram(self.program_id)
    def set_mat4(self, name: str, matrix: np.ndarray): glUniformMatrix4fv(glGetUniformLocation(self.program_id, name), 1, GL_FALSE, matrix)
    def set_vec3(self, name: str, vector: Vector3): glUniform3fv(glGetUniformLocation(self.program_id, name), 1, vector)
    def set_int(self, name: str, value: int): glUniform1i(glGetUniformLocation(self.program_id, name), value)

def _calculate_tangents_and_bitangents(vertices):
    final_vertices = []
    # Process 3 vertices at a time (one triangle)
    for i in range(0, len(vertices), 3):
        v0, v1, v2 = vertices[i], vertices[i+1], vertices[i+2]
        
        pos0, pos1, pos2 = Vector3(v0[0:3]), Vector3(v1[0:3]), Vector3(v2[0:3])
        uv0, uv1, uv2 = Vector3([v0[6], v0[7], 0]), Vector3([v1[6], v1[7], 0]), Vector3([v2[6], v2[7], 0])
        
        edge1 = pos1 - pos0
        edge2 = pos2 - pos0
        delta_uv1 = uv1 - uv0
        delta_uv2 = uv2 - uv0
        
        f = 1.0 / (delta_uv1.x * delta_uv2.y - delta_uv2.x * delta_uv1.y)
        
        tangent = Vector3([
            f * (delta_uv2.y * edge1.x - delta_uv1.y * edge2.x),
            f * (delta_uv2.y * edge1.y - delta_uv1.y * edge2.y),
            f * (delta_uv2.y * edge1.z - delta_uv1.y * edge2.z)
        ]).normalized
        
        bitangent = Vector3([
            f * (-delta_uv2.x * edge1.x + delta_uv1.x * edge2.x),
            f * (-delta_uv2.x * edge1.y + delta_uv1.x * edge2.y),
            f * (-delta_uv2.x * edge1.z + delta_uv1.x * edge2.z)
        ]).normalized
        
        # Add the calculated tangent and bitangent to each vertex of the triangle
        final_vertices.extend(list(v0) + list(tangent) + list(bitangent))
        final_vertices.extend(list(v1) + list(tangent) + list(bitangent))
        final_vertices.extend(list(v2) + list(tangent) + list(bitangent))
        
    return np.array(final_vertices, dtype=np.float32)

def load_cube_mesh() -> Mesh:
    vertices = [
        # pos              # normal           # uv
        [-0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0], [ 0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0], [ 0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0],
        [ 0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0], [-0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0], [-0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0],
        [-0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 0.0], [ 0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0], [ 0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 1.0],
        [ 0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 1.0], [-0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 1.0], [-0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 0.0],
        [-0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0], [-0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 1.0], [-0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0],
        [-0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0], [-0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0, 0.0], [-0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0],
        [ 0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0], [ 0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0], [ 0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0],
        [ 0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0], [ 0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0], [ 0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0],
        [-0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0], [ 0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0], [ 0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0],
        [ 0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0], [-0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0], [-0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0],
        [-0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0], [ 0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 1.0], [ 0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0],
        [ 0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0], [-0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0], [-0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0]
    ]
    return Mesh(_calculate_tangents_and_bitangents(vertices))

def load_quad_mesh() -> Mesh:
    vertices = [
        [-1.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0], [1.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0],
        [-1.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0], [-1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    ]
    return Mesh(_calculate_tangents_and_bitangents(vertices))

def load_sphere_mesh(radius=1.0, sectors=36, stacks=18) -> Mesh:
    sphere_vertices = []
    for i in range(stacks + 1):
        stack_angle = math.pi / 2 - i * math.pi / stacks
        xy = radius * math.cos(stack_angle)
        z = radius * math.sin(stack_angle)
        for j in range(sectors + 1):
            sector_angle = j * 2 * math.pi / sectors
            x, y = xy * math.cos(sector_angle), xy * math.sin(sector_angle)
            pos, norm, uv = [x,y,z], list(Vector3([x,y,z]).normalized), [j/sectors, i/stacks]
            sphere_vertices.append(pos + norm + uv)
    
    indices = []
    for i in range(stacks):
        k1, k2 = i * (sectors + 1), i * (sectors + 1) + sectors + 1
        for j in range(sectors):
            if i != 0: indices.extend([k1, k2, k1 + 1])
            if i != (stacks - 1): indices.extend([k1 + 1, k2, k2 + 1])
            k1 += 1; k2 += 1
    
    # De-index the vertices for tangent calculation
    unindexed_vertices = []
    for index in indices:
        unindexed_vertices.append(sphere_vertices[index])
        
    return Mesh(_calculate_tangents_and_bitangents(unindexed_vertices))