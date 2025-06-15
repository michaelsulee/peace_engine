# src/game_object.py
import numpy as np
import transform as tf
from OpenGL.GL import *

class GameObject:
    def __init__(self, mesh, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1), 
                 textured=True, is_ghost=False, is_unlit=False, 
                 casts_shadow=True, is_selectable=True): # <-- ADD is_selectable
        
        self.mesh = mesh
        self.transform = tf.Transform(position, rotation, scale)
        self.textured = textured
        self.is_ghost = is_ghost
        self.is_unlit = is_unlit
        self.casts_shadow = casts_shadow
        self.is_selectable = is_selectable # <-- STORE IT
        self.is_selected = False
        self.aabb_min = np.zeros(3, dtype=np.float32)
        self.aabb_max = np.zeros(3, dtype=np.float32)
        self._update_aabb()

    def _update_aabb(self):
        model_matrix = self.transform.get_model_matrix()
        verts = self.mesh.vertices[:, :3]
        homogeneous_verts = np.hstack([verts, np.ones((verts.shape[0], 1))])
        transformed_verts = (homogeneous_verts @ model_matrix.T)[:, :3]
        self.aabb_min = np.min(transformed_verts, axis=0)
        self.aabb_max = np.max(transformed_verts, axis=0)

    def draw(self, shader_program):
        if self.transform.is_dirty:
            self._update_aabb()
        shader_program.set_mat4("u_model", self.transform.get_model_matrix())
        
        shader_program.set_bool("u_is_ghost", self.is_ghost)
        shader_program.set_bool("u_is_selected", self.is_selected)
        shader_program.set_bool("u_textured", self.textured)
        shader_program.set_bool("u_is_unlit", self.is_unlit)

        self.mesh.draw()

    @property
    def position(self): return self.transform.position
    
    def cleanup(self):
        if self.mesh: self.mesh.cleanup()