# src/mesh.py
from OpenGL.GL import *
import numpy as np
import ctypes

class Mesh:
    """
    Represents a 3D mesh. It now handles vertices with position, normal,
    texture coordinate, tangent, and bitangent data.
    """
    def __init__(self, vertices):
        """
        Args:
            vertices (numpy.ndarray): A NumPy array of vertex data, interleaved.
            Layout: pos(3), norm(3), uv(2), tangent(3), bitangent(3)
        """
        # 14 floats per vertex (3+3+2+3+3)
        self.vert_count = len(vertices) // 14

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Stride is 14 floats * 4 bytes/float = 56 bytes
        stride = 56

        # Attribute 0: Position (3 floats)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

        # Attribute 1: Normal (3 floats)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

        # Attribute 2: Texture Coordinate (2 floats)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

        # Attribute 3: Tangent (3 floats)
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(32))

        # Attribute 4: Bitangent (3 floats)
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(44))

        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vert_count)
        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))