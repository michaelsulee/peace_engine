# src/engine.py
import pygame
from OpenGL.GL import *
from camera import Camera
from input_handler import InputHandler
from pyrr import Vector3, Vector4, matrix44
import numpy as np
import asset_loader
import texture_loader
from mesh import Mesh
import sys
import re

def lerp(v1: Vector3, v2: Vector3, factor: float) -> Vector3:
    factor = max(0.0, min(1.0, factor))
    return v1 * (1.0 - factor) + v2 * factor

class Engine:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.running = False
        self.paused = False
        
        self._initialize_pygame_and_opengl()
        
        self.clock = pygame.time.Clock()
        self.time = 0.0
        
        self.camera = Camera(Vector3([0.0, 4.0, 15.0]), self.width / self.height)
        self.input_handler = InputHandler(self, self.camera)

        # --- Load Assets ---
        self.lighting_shader = asset_loader.Shader("assets/shaders/default.vert", "assets/shaders/default.frag")
        self.skybox_shader = asset_loader.Shader("assets/shaders/skybox.vert", "assets/shaders/skybox.frag")
        self.light_source_shader = asset_loader.Shader("assets/shaders/light_source.vert", "assets/shaders/light_source.frag")
        self.ui_shader = asset_loader.Shader("assets/shaders/ui.vert", "assets/shaders/ui.frag")
        
        self.cube_mesh = asset_loader.load_cube_mesh()
        self.floor_mesh = asset_loader.load_quad_mesh()
        self.skybox_mesh = asset_loader.load_cube_mesh()
        self.sphere_mesh = asset_loader.load_sphere_mesh()
        self.ui_quad_mesh = asset_loader.load_quad_mesh()

        self.container_texture = texture_loader.generate_matte_texture(color=(255, 128, 80))
        self.floor_texture = texture_loader.generate_checkerboard_texture(width=16, height=16, c1=(60,60,60), c2=(80,80,80))
        
        try:
            self.skybox_texture = texture_loader.load_cubemap([
                f"assets/skybox/{face}.bmp" for face in ["right","left","top","bottom","front","back"]
            ])
        except FileNotFoundError as e:
            print(f"\nFATAL ERROR: {e}")
            pygame.quit()
            sys.exit()
            
        self.font = pygame.font.Font(None, 48)
        self.input_text, self.text_dirty = "", False
        self.text_texture, self.text_texture_dims = None, (0,0)
        
        prompt_surface = self.font.render("Enter Time (HH:MM):", True, (255, 255, 255))
        self.prompt_texture, w, h = texture_loader.create_texture_from_surface(prompt_surface)
        self.prompt_texture_dims = (w, h)
        self.ui_bg_texture = texture_loader.generate_matte_texture(color=(0,0,0))

        # --- State Variables ---
        self.sun_active = True
        self.sun_movement_paused = False
        self.current_time_minutes, day_duration_seconds = 480, 120
        self.time_speed = 1440.0 / day_duration_seconds
        
        floor_scale, sun_scale = 100.0, 15.0
        self.floor_model_matrix = matrix44.create_from_scale(Vector3([floor_scale] * 3), dtype=np.float32)
        self.cube_model_matrix = matrix44.create_from_translation(Vector3([0.0, 2.5, 0.0]), dtype=np.float32)
        self.sun_model_matrix = matrix44.create_from_scale(Vector3([sun_scale] * 3), dtype=np.float32)
        
        self.light_pos, self.light_color = Vector3([0.0, 0.0, 0.0]), Vector3([1.0, 1.0, 1.0])
        self.ambient_color, self.light_orbit_radius = Vector3([0.0, 0.0, 0.0]), floor_scale * 0.75

    def _initialize_pygame_and_opengl(self):
        pygame.init()
        pygame.display.set_caption("PEACE Engine v1.0")
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.mouse.set_visible(False); pygame.event.set_grab(True)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # As commanded, global culling is disabled.
        # It will be enabled temporarily only where technically necessary.
        # glEnable(GL_CULL_FACE)

    def run(self):
        self.running = True
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            self.input_handler.process_input(delta_time)
            if not self.paused: self._update(delta_time)
            self._render()
        self._cleanup()
        
    def enter_time_set_mode(self):
        self.paused = True
        self.input_text = ""
        self.text_dirty = True
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        self.input_handler.first_mouse = True

    def exit_time_set_mode(self):
        self.paused = False
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.input_handler.first_mouse = True

    def commit_time_change(self):
        try:
            match = re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', self.input_text)
            if not match: raise ValueError("Invalid format")
            hours, minutes = map(int, match.groups())
            self.current_time_minutes = hours * 60 + minutes
            print(f"Time set to {hours:02d}:{minutes:02d}.")
        except (ValueError, TypeError):
            print(f"Invalid time entered: '{self.input_text}'")
        self.exit_time_set_mode()
        
    def _update(self, delta_time):
        if not self.sun_movement_paused:
            self.current_time_minutes = (self.current_time_minutes + self.time_speed * delta_time) % 1440
        
        time_ratio = self.current_time_minutes / 1440.0
        sun_angle = time_ratio * 2.0 * np.pi
        
        self.light_pos.x = np.cos(sun_angle) * self.light_orbit_radius
        self.light_pos.z = np.sin(sun_angle) * self.light_orbit_radius
        self.light_pos.y = np.sin(time_ratio * np.pi) * (self.light_orbit_radius * 0.5) + 5.0
    
    def _update_lighting_and_colors(self):
        time_ratio = self.current_time_minutes / 1440.0
        sunrise_color = Vector3([1.0, 0.4, 0.2]); noon_color = Vector3([1.0, 1.0, 0.9]); sunset_color = Vector3([1.0, 0.4, 0.2]); night_color = Vector3([0.6, 0.7, 0.9])
        sunrise_ambient = Vector3([0.3, 0.2, 0.2]); noon_ambient = Vector3([0.5, 0.5, 0.5]); night_ambient = Vector3([0.05, 0.05, 0.15])
        sunrise_sky = Vector3([0.6, 0.3, 0.3]); noon_sky = Vector3([0.5, 0.8, 1.0]); night_sky = Vector3([0.01, 0.01, 0.05])

        if 0.20 < time_ratio < 0.30:
            interp = (time_ratio - 0.20) / 0.10
            self.light_color = lerp(night_color, sunrise_color, interp)
            self.ambient_color = lerp(night_ambient, sunrise_ambient, interp)
            glClearColor(*lerp(night_sky, sunrise_sky, interp), 1.0)
        elif 0.30 <= time_ratio <= 0.70:
            interp = (time_ratio - 0.30) / 0.40
            if interp < 0.5:
                self.light_color = lerp(sunrise_color, noon_color, interp * 2)
                self.ambient_color = lerp(sunrise_ambient, noon_ambient, interp * 2)
                glClearColor(*lerp(sunrise_sky, noon_sky, interp * 2), 1.0)
            else:
                self.light_color = lerp(noon_color, sunset_color, (interp - 0.5) * 2)
                self.ambient_color = lerp(noon_ambient, sunrise_ambient, (interp - 0.5) * 2)
                glClearColor(*lerp(noon_sky, sunrise_sky, (interp - 0.5) * 2), 1.0)
        elif 0.70 < time_ratio < 0.80:
            interp = (time_ratio - 0.70) / 0.10
            self.light_color = lerp(sunset_color, night_color, interp)
            self.ambient_color = lerp(sunrise_ambient, night_ambient, interp)
            glClearColor(*lerp(sunrise_sky, night_sky, interp), 1.0)
        else:
            self.light_color = night_color
            self.ambient_color = night_ambient
            glClearColor(*night_sky, 1.0)
            
    def _render(self):
        self._update_lighting_and_colors()
        
        # --- MAIN RENDER PASS ---
        glViewport(0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        projection, view = self.camera.get_projection_matrix(), self.camera.get_view_matrix()
        
        # --- Draw Scene Objects ---
        self.lighting_shader.use()
        self.lighting_shader.set_mat4("projection", projection); self.lighting_shader.set_mat4("view", view)
        self.lighting_shader.set_vec3("lightPos", self.light_pos); self.lighting_shader.set_vec3("viewPos", self.camera.position)
        self.lighting_shader.set_vec3("lightColor", self.light_color if self.sun_active else Vector3([0.0,0.0,0.0]))
        self.lighting_shader.set_vec3("ambientColor", self.ambient_color)
        self.lighting_shader.set_int("objectTexture", 0)
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.container_texture)
        self.lighting_shader.set_mat4("model", self.cube_model_matrix)
        self.cube_mesh.draw()
        
        glBindTexture(GL_TEXTURE_2D, self.floor_texture)
        self.lighting_shader.set_mat4("model", self.floor_model_matrix)
        self.floor_mesh.draw()
        
        # --- Draw the Sun ---
        if self.sun_active:
            self.light_source_shader.use()
            sun_world_matrix = matrix44.multiply(matrix44.create_from_translation(self.light_pos), self.sun_model_matrix)
            self.light_source_shader.set_mat4("projection", projection); self.light_source_shader.set_mat4("view", view)
            self.light_source_shader.set_mat4("model", sun_world_matrix); self.light_source_shader.set_vec3("lightColor", self.light_color)
            self.sphere_mesh.draw()

        # --- Draw the Skybox ---
        glDepthFunc(GL_LEQUAL)
        self.skybox_shader.use()
        view_no_translation = matrix44.create_from_matrix33(view[:3,:3])
        self.skybox_shader.set_mat4("view", view_no_translation); self.skybox_shader.set_mat4("projection", projection)
        glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture); self.skybox_shader.set_int("skybox", 0)
        glDepthFunc(GL_LESS)
        
        # --- Draw UI ---
        if self.paused:
            self._render_ui()

        pygame.display.flip()

    def _render_ui(self):
        # This method is unchanged
        ...

    def _cleanup(self):
        valid_textures = [tex for tex in [self.container_texture, self.floor_texture, self.skybox_texture, self.prompt_texture, self.text_texture, self.ui_bg_texture] if tex is not None]
        if valid_textures:
            glDeleteTextures(len(valid_textures), valid_textures)
        
        self.lighting_shader.destroy()
        self.skybox_shader.destroy()
        self.light_source_shader.destroy()
        self.ui_shader.destroy()

        self.cube_mesh.destroy()
        self.floor_mesh.destroy()
        self.skybox_mesh.destroy()
        self.sphere_mesh.destroy()
        self.ui_quad_mesh.destroy()
        pygame.quit()