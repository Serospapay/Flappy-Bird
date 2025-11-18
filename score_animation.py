"""
@file: score_animation.py
@description: Система анімацій рахунку (pop-up ефект при наборі очок).
@dependencies: pygame, math
@created: 2024-12-19
"""

import pygame
import math

class ScoreAnimation:
    """Анімація рахунку з pop-up ефектом."""
    
    def __init__(self, x, y, score_change, color=(255, 255, 150), duration=60):
        """
        Ініціалізація анімації рахунку.
        
        Args:
            x: float - Початкова координата X
            y: float - Початкова координата Y
            score_change: int - Зміна рахунку (+1, +2, тощо)
            color: tuple - Колір тексту
            duration: int - Тривалість анімації в кадрах
        """
        self.x = x
        self.start_y = y
        self.y = y
        self.score_change = score_change
        self.color = color
        self.duration = duration
        self.current_time = 0
        self.alpha = 255
        self.scale = 1.0
        
    def update(self):
        """Оновлення анімації."""
        self.current_time += 1
        
        if self.current_time >= self.duration:
            return False
        
        # Pop-up ефект (вгору з затуханням)
        progress = self.current_time / self.duration
        
        # Рух вгору
        self.y = self.start_y - (progress * 50)
        
        # Масштабування (спочатку великий, потім менший)
        if progress < 0.3:
            self.scale = 1.0 + (progress / 0.3) * 0.5  # Від 1.0 до 1.5
        else:
            self.scale = 1.5 - ((progress - 0.3) / 0.7) * 0.3  # Від 1.5 до 1.2
        
        # Затухання прозорості
        if progress > 0.5:
            self.alpha = int(255 * (1 - (progress - 0.5) * 2))
        else:
            self.alpha = 255
        
        return True
    
    def draw(self, screen, font):
        """
        Малювання анімації рахунку.
        
        Args:
            screen: pygame.Surface - Екран для малювання
            font: pygame.font.Font - Шрифт
        """
        if self.alpha <= 0:
            return
        
        # Текст з знаком +
        text = f"+{self.score_change}"
        text_surface = font.render(text, True, self.color)
        
        # Масштабування
        if self.scale != 1.0:
            new_size = (int(text_surface.get_width() * self.scale),
                       int(text_surface.get_height() * self.scale))
            text_surface = pygame.transform.scale(text_surface, new_size)
        
        # Застосування прозорості
        if self.alpha < 255:
            text_surface.set_alpha(self.alpha)
        
        # Позиція
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        
        # Тінь тексту
        shadow_surface = font.render(text, True, (0, 0, 0))
        if self.scale != 1.0:
            shadow_surface = pygame.transform.scale(shadow_surface, new_size)
        if self.alpha < 255:
            shadow_surface.set_alpha(self.alpha)
        shadow_rect = shadow_surface.get_rect(center=(self.x + 2, self.y + 2))
        screen.blit(shadow_surface, shadow_rect)
        
        screen.blit(text_surface, text_rect)

class ScoreAnimationSystem:
    """Система керування анімаціями рахунку."""
    
    def __init__(self):
        """Ініціалізація системи анімацій."""
        self.animations = []
    
    def add_score_change(self, x, y, score_change, color=(255, 255, 150)):
        """
        Додати анімацію зміни рахунку.
        
        Args:
            x: float - Координата X
            y: float - Координата Y
            score_change: int - Зміна рахунку
            color: tuple - Колір тексту
        """
        animation = ScoreAnimation(x, y, score_change, color)
        self.animations.append(animation)
    
    def update(self):
        """Оновлення всіх анімацій."""
        self.animations = [anim for anim in self.animations if anim.update()]
    
    def draw(self, screen, font):
        """
        Малювання всіх анімацій.
        
        Args:
            screen: pygame.Surface - Екран для малювання
            font: pygame.font.Font - Шрифт
        """
        for animation in self.animations:
            animation.draw(screen, font)

