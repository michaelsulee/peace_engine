# src/engine.py
import pygame
from OpenGL.GL import *
import numpy as np
import ctypes

import camera, input_handler, scene, editor, frustum, raycaster, math_utils, asset_loader, ui

class Engine:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.SHADOW_WIDTH, self.SHADOW_HEIGHT = 2048, 2048
        self.depth_map_fbo = None
        self.depth_map_texture = None
        self.depth_shader = None
        
        self._initialize_pygame()
        self.clock = pygame.time.Clock()
        self.running = True
        self.mouse_grabbed = True
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        
        self._initialize_engine_systems()
        self._load_resources()

    def _initialize_pygame(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption("PEACE Engine")
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST); glEnable(GL_CULL_FACE); glViewport(0, 0, self.width, self.height)

    def _initialize_engine_systems(self):
        print("Initializing PEACE Engine systems...")
        self.camera = camera.Camera(aspect=self.width/self.height)
        self.scene = scene.Scene()
        self.editor = editor.Editor(self.scene)
        self.frustum = frustum.Frustum()
        self.projection_matrix = math_utils.perspective_matrix(45, self.width/self.height, 0.01, 500.0)
        self.raycaster = raycaster.Raycaster(self.camera, self.projection_matrix)
        self.input_handler = input_handler.InputHandler(self)

    def _load_resources(self):
        print("Loading resources...")
        self.forward_shader = asset_loader.Shader("assets/shaders/default.vert", "assets/shaders/default.frag")
        self.skybox_shader = asset_loader.Shader("assets/shaders/skybox.vert", "assets/shaders/skybox.frag")
        self.depth_shader = asset_loader.Shader("assets/shaders/depth_shader.vert", "assets/shaders/depth_shader.frag")
        
        self._setup_shadow_map()
        self._setup_skybox()
        self._setup_ui()
        
        print("Loading initial scene...")
        self.editor.add_primitive(primitive_type='cube', position=[0, -1, 0], scale=[200, 1, 200], textured=False, is_selectable=False)
        self.editor.add_primitive(primitive_type='cube', position=[0, 0.5, 0])
        
        self.scene.sun = self.editor.add_primitive('sphere', scale=[2, 2, 2], is_unlit=True, casts_shadow=False, is_selectable=False)
        print("Engine ready.")

    def _setup_shadow_map(self):
        print("Setting up shadow map framebuffer...")
        self.depth_map_fbo = glGenFramebuffers(1)
        self.depth_map_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_map_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.SHADOW_WIDTH, self.SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32))
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_map_texture, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer for shadow map is not complete!")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def _setup_skybox(self):
        skybox_faces = [f'assets/skybox/{face}.bmp' for face in ['right', 'left', 'top', 'bottom', 'front', 'back']]
        self.skybox_texture = asset_loader.load_cubemap(skybox_faces)
        skybox_verts = np.array([-1,-1,1, 1,-1,1, 1,1,1, 1,1,1, -1,1,1, -1,-1,1, -1,-1,-1, -1,1,-1, 1,1,-1, 1,1,-1, 1,-1,-1, -1,-1,-1, -1,1,-1, -1,1,1, 1,1,1, 1,1,1, 1,1,-1, -1,1,-1, -1,-1,-1, 1,-1,-1, 1,-1,1, 1,-1,1, -1,-1,1, -1,-1,-1, 1,-1,-1, 1,1,-1, 1,1,1, 1,1,1, 1,-1,1, 1,-1,-1, -1,-1,-1, -1,-1,1, -1,1,1, -1,1,1, -1,1,-1, -1,-1,-1,], dtype=np.float32)
        self.skybox_vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(self.skybox_vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, skybox_verts.nbytes, skybox_verts, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * ctypes.sizeof(GLfloat), None)
        glBindVertexArray(0)

    def _setup_ui(self):
        self.text_renderer = ui.TextRenderer(None, 24)
        self.projection_matrix_ui = math_utils.ortho_matrix(0, self.width, self.height, 0, -1, 1)
        drawer_width = 250
        self.asset_drawer = ui.SimplePanel(-drawer_width, 0, drawer_width, self.height, (0.1, 0.1, 0.15, 0.9))
        self.asset_buttons = [ui.SimpleButton(25, self.height - 80, 200, 40, "Cube", self.text_renderer, lambda: self.editor.start_placement('cube'))]
        self.context_menu_panel = ui.SimplePanel(0, 0, 150, 100, (0.15, 0.15, 0.2, 0.95))
        self.context_menu_buttons = {"Delete": ui.SimpleButton(0, 0, 140, 30, "Delete", self.text_renderer, self.delete_selected_object),"Copy": ui.SimpleButton(0, 0, 140, 30, "Copy", self.text_renderer, self.copy_selected_object)}
        self.context_menu_active = False; self.selected_object = None
        self.show_controls = True; self.asset_drawer_open = False

    ### --- MAIN GAME LOOP AND HELPER METHODS RESTORED --- ###

    def run(self):
        """The main engine loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.input_handler.handle_events()
            self.input_handler.handle_continuous_input(dt)
            self._update(dt)
            self._render()
        self._cleanup()
        
    def _render(self):
        """Main render function, orchestrating the two-pass shadow mapping."""
        light_projection = math_utils.ortho_matrix(-35, 35, -35, 35, 1.0, 100.0)
        light_view = math_utils.look_at(self.scene.light_pos, np.array([0,0,0], dtype=np.float32), np.array([0,1,0], dtype=np.float32))
        light_space_matrix = light_projection @ light_view
        
        # --- PASS 1: RENDER TO DEPTH MAP ---
        glViewport(0, 0, self.SHADOW_WIDTH, self.SHADOW_HEIGHT)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glClear(GL_DEPTH_BUFFER_BIT)
        glCullFace(GL_BACK) # Use default culling for stability
        
        self.depth_shader.use()
        self.depth_shader.set_mat4("u_lightSpaceMatrix", light_space_matrix)
        self.scene.draw(self.depth_shader, frustum=None, render_pass='shadow')
        
        # --- PASS 2: RENDER FINAL SCENE ---
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.52, 0.8, 0.92, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Ensure culling is default
        glCullFace(GL_BACK)

        view_matrix = self.camera.get_view_matrix()
        
        # Draw the main scene objects with shadows
        self.forward_shader.use()
        self.forward_shader.set_mat4("u_projection", self.projection_matrix)
        self.forward_shader.set_mat4("u_view", view_matrix)
        self.forward_shader.set_vec3("u_viewPos", self.camera.position)
        self.forward_shader.set_vec3("u_lightPos", self.scene.light_pos)
        self.forward_shader.set_mat4("u_lightSpaceMatrix", light_space_matrix)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.depth_map_texture)
        self.forward_shader.set_int("shadowMap", 1)
        self.scene.draw(self.forward_shader, self.frustum, render_pass='main')
        
        self._render_skybox(view_matrix)

        pygame.display.flip()

    def _render_skybox(self, view_matrix):
        """Helper function to isolate skybox rendering logic."""
        if self.skybox_texture is None:
            glDepthFunc(GL_LEQUAL)
            glCullFace(GL_FRONT)
            self.skybox_shader.use()
            self.skybox_shader.set_bool("u_hasSkyboxTexture", False)
            skybox_view = view_matrix.copy(); skybox_view[3, :3] = 0
            self.skybox_shader.set_mat4("view", skybox_view)
            self.skybox_shader.set_mat4("projection", self.projection_matrix)
            glBindVertexArray(self.skybox_vao); glDrawArrays(GL_TRIANGLES, 0, 36)
            glCullFace(GL_BACK); glDepthFunc(GL_LESS)
            return

        glDepthFunc(GL_LEQUAL)
        glCullFace(GL_FRONT)
        self.skybox_shader.use()
        self.skybox_shader.set_bool("u_hasSkyboxTexture", True)
        skybox_view = view_matrix.copy(); skybox_view[3, :3] = 0
        self.skybox_shader.set_mat4("view", skybox_view)
        self.skybox_shader.set_mat4("projection", self.projection_matrix)
        glActiveTexture(GL_TEXTURE0)
        self.skybox_shader.set_int("skybox", 0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture)
        glBindVertexArray(self.skybox_vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glCullFace(GL_BACK)
        glDepthFunc(GL_LESS)

    def _update(self, dt):
        view_matrix = self.camera.get_view_matrix()
        self.raycaster.update_matrices(view_matrix)
        self.frustum.update(self.projection_matrix @ view_matrix)
        
        if self.scene.sun:
            self.scene.sun.transform.set_position(self.scene.light_pos)

        if self.editor.placement_mode_active:
            ray_dir = self.raycaster.get_ray_from_mouse(*pygame.mouse.get_pos(), self.width, self.height)
            intersection = self.raycaster.intersect_ray_plane(self.camera.position, ray_dir)
            if intersection is not None: self.editor.update_ghost_position(intersection)
        if not (self.context_menu_active or self.asset_drawer_open or self.editor.placement_mode_active):
            ray_dir = self.raycaster.get_ray_from_center()
            closest_hit_dist = float('inf')
            self.selected_object = None
            for obj in self.scene.game_objects:
                if obj.is_selectable and not obj.is_ghost and self.raycaster.intersect_ray_aabb(self.camera.position, ray_dir, obj.aabb_min, obj.aabb_max):
                    dist = np.linalg.norm(obj.position - self.camera.position)
                    if dist < closest_hit_dist: closest_hit_dist, self.selected_object = dist, obj
        self.scene.update_selection(self.selected_object)

    def _cleanup(self):
        print("Cleaning up resources...")
        self.scene.cleanup()
        self.forward_shader.cleanup()
        self.skybox_shader.cleanup()
        if self.depth_shader: self.depth_shader.cleanup()
        for mesh in self.editor.primitive_meshes.values(): mesh.cleanup()
        glDeleteVertexArrays(1, [self.skybox_vao])
        if self.skybox_texture: glDeleteTextures(1, [self.skybox_texture])
        if self.depth_map_fbo: glDeleteFramebuffers(1, [self.depth_map_fbo])
        if self.depth_map_texture: glDeleteTextures(1, [self.depth_map_texture])
        pygame.quit()
    
    def toggle_mouse_grab(self):
        self.mouse_grabbed = not self.mouse_grabbed
        pygame.mouse.set_visible(not self.mouse_grabbed)
        pygame.event.set_grab(self.mouse_grabbed)
    def toggle_asset_drawer(self):
        self.asset_drawer_open = not self.asset_drawer_open
        if not self.asset_drawer_open: self.editor.cancel_placement()
    def delete_selected_object(self):
        if self.selected_object: self.scene.remove_object(self.selected_object)
        self.selected_object = None
        self.context_menu_active = False
    def copy_selected_object(self):
        if self.selected_object: self.editor.add_primitive(primitive_type='cube', position=self.selected_object.position + np.array([2, 0, 0]))
        self.context_menu_active = False