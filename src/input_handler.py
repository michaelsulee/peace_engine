# src/input_handler.py
import pygame
import numpy as np

class InputHandler:
    def __init__(self, engine):
        self.engine = engine
        self.camera = engine.camera
        self.editor = engine.editor
        self.scene = engine.scene

        self.light_angle = np.deg2rad(135.0) # Start with light behind and to the side
        self.light_radius = 40.0
        self.light_height = 40.0

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.engine.running = False
            if self.engine.context_menu_active and any(b.handle_event(event, mouse_pos) for b in self.engine.context_menu_buttons.values()): self.engine.context_menu_active = False; continue
            if self.engine.asset_drawer_open and any(b.handle_event(event, mouse_pos) for b in self.engine.asset_buttons): self.engine.asset_drawer_open = False; continue
            if self.editor.placement_mode_active and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: self.editor.place_object()
                elif event.button == 3: self.editor.cancel_placement()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.engine.running = False
                elif event.key == pygame.K_TAB: self.engine.toggle_mouse_grab()
                elif event.key == pygame.K_9: self.engine.toggle_asset_drawer()
                elif event.key == pygame.K_l: self.engine.show_controls = not self.engine.show_controls
                elif event.key == pygame.K_e and self.engine.selected_object: self.engine.context_menu_active = not self.engine.context_menu_active

    def handle_continuous_input(self, dt):
        if self.engine.mouse_grabbed:
            self.camera.process_keyboard(dt)
            self.camera.process_mouse_movement(*pygame.mouse.get_rel())
        
        keys = pygame.key.get_pressed()
        angle_speed = 2.0 * dt
        height_speed = 20.0 * dt

        if keys[pygame.K_LEFT]: self.light_angle -= angle_speed
        if keys[pygame.K_RIGHT]: self.light_angle += angle_speed
        # Re-implement up/down controls
        if keys[pygame.K_PAGEUP]: self.light_height += height_speed
        if keys[pygame.K_PAGEDOWN]: self.light_height -= height_speed
        
        self.scene.light_pos[0] = self.light_radius * np.cos(self.light_angle)
        self.scene.light_pos[2] = self.light_radius * np.sin(self.light_angle)
        self.scene.light_pos[1] = self.light_height