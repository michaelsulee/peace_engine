# src/scene.py
import numpy as np

class Scene:
    def __init__(self):
        self.game_objects = []
        self.light_pos = np.array([-25.0, 40.0, -25.0], dtype=np.float32)
        self.sun = None

    def add_object(self, game_object):
        self.game_objects.append(game_object)

    def remove_object(self, game_object):
        if game_object in self.game_objects:
            self.game_objects.remove(game_object)

    def update_selection(self, selected_obj):
        for obj in self.game_objects:
            obj.is_selected = (obj == selected_obj)

    def draw(self, shader, frustum, render_pass='main'):
        """Draws objects, filtering based on render pass."""
        for obj in self.game_objects:
            # For the shadow pass, only draw objects that cast shadows
            if render_pass == 'shadow' and not obj.casts_shadow:
                continue
            
            # For the main pass, use frustum culling
            if frustum is None or frustum.is_box_in_frustum(obj.aabb_min, obj.aabb_max):
                obj.draw(shader)

    def cleanup(self):
        for obj in self.game_objects: pass
        self.game_objects.clear()