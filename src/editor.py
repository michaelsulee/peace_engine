# src/editor.py
from game_object import GameObject  # <-- IMPORT FIX: More direct import
import asset_loader
import numpy as np

class Editor:
    def __init__(self, scene):
        self.scene = scene
        self.placement_mode_active = False
        self.ghost_object = None
        self.primitive_type = None
        self.primitive_meshes = {
            'cube': asset_loader.generate_cube_mesh(),
            'sphere': asset_loader.generate_sphere_mesh()
        }

    def start_placement(self, primitive_type):
        if primitive_type not in self.primitive_meshes:
            print(f"Error: Primitive type '{primitive_type}' not supported.")
            return
            
        self.cancel_placement()
        self.primitive_type = primitive_type
        # Use direct class name now
        self.ghost_object = GameObject(self.primitive_meshes[primitive_type], is_ghost=True)
        self.scene.add_object(self.ghost_object)
        self.placement_mode_active = True

    def update_ghost_position(self, position):
        if self.ghost_object:
            self.ghost_object.transform.set_position(position)

    def place_object(self):
        if self.ghost_object:
            self.add_primitive(primitive_type=self.primitive_type, position=self.ghost_object.position)
            self.scene.remove_object(self.ghost_object)
            self.ghost_object = None
            self.placement_mode_active = False

    def cancel_placement(self):
        if self.ghost_object:
            self.scene.remove_object(self.ghost_object)
            self.ghost_object = None
        self.placement_mode_active = False

    def add_primitive(self, primitive_type, **kwargs):
        if primitive_type in self.primitive_meshes:
            mesh = self.primitive_meshes[primitive_type]
            # Use direct class name now
            obj = GameObject(mesh, **kwargs)
            self.scene.add_object(obj)
            return obj
        print(f"Warning: Primitive type '{primitive_type}' not found in editor cache.")
        return None