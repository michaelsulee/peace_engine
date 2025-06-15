# src/input_handler.py
import pygame
import numpy as np

class InputHandler:
    def __init__(self, engine, camera):
        self.engine = engine
        self.camera = camera
        self.first_mouse = True

    def process_input(self, delta_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.engine.paused:
                    self._handle_ui_input(event)
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.engine.running = False
                    if event.key == pygame.K_EQUALS:
                        self.engine.enter_time_set_mode()
                    if event.key == pygame.K_BACKSLASH:
                        self.engine.sun_active = not self.engine.sun_active
                        status = "ON" if self.engine.sun_active else "OFF"
                        print(f"Sunlight toggled {status}.")
                    if event.key == pygame.K_QUOTE:
                        self.engine.sun_movement_paused = not self.engine.sun_movement_paused
                        status = "paused" if self.engine.sun_movement_paused else "resumed"
                        print(f"Sun movement {status}.")

        if not self.engine.paused:
            self._handle_mouse_movement()
            self._handle_key_presses(delta_time)
    
    def _handle_ui_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.engine.exit_time_set_mode()
        elif event.key == pygame.K_RETURN:
            self.engine.commit_time_change()
        elif event.key == pygame.K_BACKSPACE:
            self.engine.input_text = self.engine.input_text[:-1]
            self.engine.text_dirty = True
        elif len(self.engine.input_text) < 5:
            if event.unicode.isdigit() or event.unicode == ':':
                self.engine.input_text += event.unicode
                self.engine.text_dirty = True

    def _handle_mouse_movement(self):
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        if self.first_mouse:
            self.first_mouse = False
            return
        self.camera.process_mouse_movement(mouse_dx, -mouse_dy)

    def _handle_key_presses(self, delta_time):
        keys = pygame.key.get_pressed()
        
        # Camera movement
        if keys[pygame.K_w]: self.camera.process_keyboard("FORWARD", delta_time)
        if keys[pygame.K_s]: self.camera.process_keyboard("BACKWARD", delta_time)
        if keys[pygame.K_a]: self.camera.process_keyboard("LEFT", delta_time)
        if keys[pygame.K_d]: self.camera.process_keyboard("RIGHT", delta_time)
        if keys[pygame.K_SPACE]: self.camera.process_keyboard("UP", delta_time)
        if keys[pygame.K_LCTRL] or keys[pygame.K_LSHIFT]: self.camera.process_keyboard("DOWN", delta_time)