"""
@file: flash_effects.py
@description: Система спалахів/блимань при важливих подіях (новий рекорд, досягнення, тощо).
@dependencies: pygame, math
@created: 2024-12-19
"""

import pygame
import math

class FlashEffect:
    """Один ефект спалаху."""
    
    def __init__(self, color=(255, 255, 255), duration=30, intensity=200, mode='flash'):
        """
        Ініціалізація ефекту спалаху.
        
        Args:
            color: tuple - Колір спалаху (R, G, B)
            duration: int - Тривалість в кадрах
            intensity: int - Інтенсивність (0-255)
            mode: str - Режим ('flash', 'pulse', 'fade')
        """
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.intensity = intensity
        self.mode = mode
        self.alpha = 0
    
    def update(self):
        """Оновлення ефекту."""
        self.duration -= 1
        
        if self.duration <= 0:
            return False
        
        progress = 1.0 - (self.duration / self.max_duration)
        
        if self.mode == 'flash':
            # Різкий спалах, що швидко затухає
            if progress < 0.3:
                self.alpha = int(self.intensity * (progress / 0.3))
            else:
                self.alpha = int(self.intensity * (1 - (progress - 0.3) / 0.7))
        
        elif self.mode == 'pulse':
            # Пульсація
            pulse = math.sin(progress * math.pi * 4) * 0.5 + 0.5
            self.alpha = int(self.intensity * pulse)
        
        elif self.mode == 'fade':
            # Плавне затухання
            self.alpha = int(self.intensity * (1 - progress))
        
        return True
    
    def draw(self, screen):
        """
        Малювання ефекту спалаху.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        if self.alpha <= 0:
            return
        
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, self.alpha))
        screen.blit(overlay, (0, 0))

class FlashSystem:
    """Система керування ефектами спалахів."""
    
    def __init__(self):
        """Ініціалізація системи спалахів."""
        self.effects = []
    
    def add_flash(self, color=(255, 255, 255), duration=30, intensity=200, mode='flash'):
        """
        Додати ефект спалаху.
        
        Args:
            color: tuple - Колір спалаху
            duration: int - Тривалість в кадрах
            intensity: int - Інтенсивність
            mode: str - Режим ('flash', 'pulse', 'fade')
        """
        effect = FlashEffect(color, duration, intensity, mode)
        self.effects.append(effect)
    
    def add_achievement_flash(self):
        """Додати ефект спалаху при отриманні досягнення."""
        self.add_flash(color=(255, 215, 0), duration=40, intensity=150, mode='pulse')
    
    def add_record_flash(self):
        """Додати ефект спалаху при новому рекорді."""
        self.add_flash(color=(255, 255, 100), duration=60, intensity=180, mode='flash')
    
    def add_score_flash(self):
        """Додати короткий спалах при наборі очок."""
        self.add_flash(color=(150, 255, 150), duration=15, intensity=100, mode='flash')
    
    def add_danger_flash(self):
        """Додати червоний спалах при небезпеці."""
        self.add_flash(color=(255, 100, 100), duration=20, intensity=120, mode='pulse')
    
    def update(self):
        """Оновлення всіх ефектів."""
        self.effects = [effect for effect in self.effects if effect.update()]
    
    def draw(self, screen):
        """
        Малювання всіх ефектів.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        # Малюємо в зворотному порядку (останній доданий - зверху)
        for effect in reversed(self.effects):
            effect.draw(screen)

