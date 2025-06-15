# src/mesh.py
import numpy as np
from OpenGL.GL import *
import ctypes

class Mesh:
    """Handles low-level vertex data and OpenGL buffer objects (VAO, VBO)."""
    def __init__(self, vertices):
        # Expects vertices in format: [pos_x, pos_y, pos_z, norm_x, norm_y, norm_z, tex_u, tex_v]
        
        # Reshape the flat list of vertices into a 2D array where each row is a vertex.
        # The '-1' tells numpy to automatically calculate the number of rows.
        self.vertices = np.array(vertices, dtype=np.float32).reshape(-1, 8)
        
        self.vertex_count = len(self.vertices)
        
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self._setup_mesh()

    def _setup_mesh(self):
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        stride = 8 * sizeof(GLfloat)
        # Vertex Positions
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        # Vertex Normals
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * sizeof(GLfloat)))
        # Vertex Texture Coords
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * sizeof(GLfloat)))
        
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    def cleanup(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])