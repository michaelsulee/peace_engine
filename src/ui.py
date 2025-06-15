# src/ui.py
import pygame
import pygame.freetype
import numpy as np
from OpenGL.GL import *
import asset_loader

class TextRenderer:
    """A placeholder for a more complex text rendering system."""
    def __init__(self, font_path, size, color=(255, 255, 255)):
        # In a real app, provide a path to a .ttf file in assets/fonts
        # pygame.freetype.init()
        # self.font = pygame.freetype.Font(font_path, size)
        # self.color = color
        pass

    def render_text(self, text, x, y, size, color):
        # This is a conceptual function. A real implementation would involve
        # creating textures from rendered text and drawing them on quads.
        # For now, we will rely on the engine's original logic for simplicity.
        pass
    def cleanup(self): pass

class SimplePanel:
    """A simple, non-rendering panel to hold UI state."""
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color
    def set_position(self, x, y):
        self.rect.x, self.rect.y = x, y
    def draw(self, proj_matrix, ui_shader):
        # A full implementation would draw a colored quad here.
        pass
    def cleanup(self): pass

class SimpleButton(SimplePanel):
    """A simple button that handles clicks."""
    def __init__(self, x, y, w, h, text, text_renderer, callback):
        super().__init__(x,y,w,h, (0.3,0.3,0.7,0.9))
        self.text = text
        self.callback = callback
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(mouse_pos):
            if self.callback:
                self.callback()
            return True
        return False