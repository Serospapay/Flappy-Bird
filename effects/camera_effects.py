"""
@file: camera_effects.py
@description: Система ефектів камери (shake, fade) для покращення UX та візуальних ефектів.
@dependencies: pygame, math
@created: 2024-12-19
"""

import pygame
import math
import random

class CameraEffects:
    """Система візуальних ефектів камери."""
    
    def __init__(self):
        """Ініціалізація системи ефектів."""
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_intensity = 0
        self.shake_duration = 0
        
        self.fade_alpha = 0
        self.fade_duration = 0
        self.fade_current = 0
        self.fade_target = 0
        self.fade_speed = 0
    
    def add_shake(self, intensity=10, duration=10):
        """
        Додати ефект трясіння камери (shake).
        
        Args:
            intensity: float - Інтенсивність трясіння
            duration: int - Тривалість в кадрах
        """
        if self.shake_duration < duration:
            self.shake_intensity = intensity
            self.shake_duration = duration
    
    def update(self):
        """Оновлення ефектів камери."""
        # Shake ефект
        if self.shake_duration > 0:
            # Випадкове зміщення з затуханням
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            
            # Затухання
            self.shake_duration -= 1
            self.shake_intensity *= 0.9
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        # Fade ефект
        if self.fade_duration > 0:
            self.fade_current += self.fade_speed
            self.fade_alpha = int(self.fade_current)
            
            if self.fade_speed > 0 and self.fade_current >= self.fade_target:
                self.fade_alpha = int(self.fade_target)
                self.fade_duration = 0
            elif self.fade_speed < 0 and self.fade_current <= self.fade_target:
                self.fade_alpha = int(self.fade_target)
                self.fade_duration = 0
            
            self.fade_duration -= 1
    
    def fade_in(self, duration=30):
        """
        Почати fade in ефект (з'явлення).
        
        Args:
            duration: int - Тривалість в кадрах
        """
        self.fade_target = 0
        self.fade_duration = duration
        if duration > 0:
            self.fade_speed = -255 / duration
        else:
            self.fade_alpha = 0
    
    def fade_out(self, duration=30):
        """
        Почати fade out ефект (зникнення).
        
        Args:
            duration: int - Тривалість в кадрах
        """
        self.fade_target = 255
        self.fade_duration = duration
        if duration > 0:
            self.fade_speed = 255 / duration
        else:
            self.fade_alpha = 255
    
    def apply_shake(self, screen, original_surface):
        """
        Застосувати shake ефект до екрану.
        
        Args:
            screen: pygame.Surface - Цільовий екран
            original_surface: pygame.Surface - Оригінальна поверхня
        """
        if self.shake_offset_x != 0 or self.shake_offset_y != 0:
            screen.blit(original_surface, (self.shake_offset_x, self.shake_offset_y))
            return True
        return False
    
    def draw_fade(self, screen):
        """
        Малювання fade overlay.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, self.fade_alpha))
            screen.blit(fade_surface, (0, 0))
    
    def is_fading(self):
        """Перевірка чи відбувається fade."""
        return self.fade_duration > 0

