"""
@file: background.py
@description: Паралакс фон з багатошаровою прокруткою для ефекту глибини.
@dependencies: pygame, random
@created: 2024-12-19
"""

import pygame
import random

class ParallaxLayer:
    """Один шар паралаксу."""
    
    def __init__(self, width, height, color, speed, offset_y=0):
        """
        Ініціалізація шару.
        
        Args:
            width: int - Ширина шару
            height: int - Висота шару
            color: tuple - Колір шару
            speed: float - Швидкість прокрутки
            offset_y: int - Зміщення по Y
        """
        self.width = width
        self.height = height
        self.color = color
        self.speed = speed
        self.offset_y = offset_y
        self.x = 0
        
        # Створення поверхні шару
        self.surface = pygame.Surface((width, height))
        self._draw_pattern()
    
    def _draw_pattern(self):
        """Малювання візерунка шару."""
        self.surface.fill(self.color)
        
        # Додаємо візерунок (хмари, об'єкти)
        if len(self.color) >= 3:
            # Більш світлий колір для візерунка
            pattern_color = tuple(min(255, c + 20) for c in self.color[:3])
            
            # Прості хмари/об'єкти
            for i in range(5):
                x = (i * self.width // 5) + random.randint(0, 100)
                y = random.randint(0, self.height // 2)
                size = random.randint(30, 80)
                pygame.draw.ellipse(self.surface, pattern_color, (x, y, size, size // 2))
    
    def update(self, delta_x):
        """Оновлення позиції шару."""
        self.x -= self.speed * delta_x
        if self.x <= -self.width:
            self.x = 0
    
    def draw(self, screen):
        """
        Малювання шару.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        # Малювання двох копій для безшовного скролу
        screen.blit(self.surface, (self.x, self.offset_y))
        screen.blit(self.surface, (self.x + self.width, self.offset_y))

class ParallaxBackground:
    """Паралакс фон з багатьма шарами."""
    
    def __init__(self, screen_width, screen_height):
        """
        Ініціалізація паралакс фону.
        
        Args:
            screen_width: int - Ширина екрану
            screen_height: int - Висота екрану
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Створення шарів (від найдальшого до найближчого)
        self.layers = [
            ParallaxLayer(
                screen_width, screen_height,
                (135, 206, 250),  # Небесно-блакитний (фон)
                0.1, 0
            ),
            ParallaxLayer(
                screen_width, screen_height // 2,
                (173, 216, 230),  # Світло-блакитний (дальні хмари)
                0.3, 0
            ),
            ParallaxLayer(
                screen_width, screen_height // 3,
                (176, 224, 230),  # Порошково-блакитний (середні хмари)
                0.5, screen_height // 4
            ),
            ParallaxLayer(
                screen_width, screen_height // 4,
                (230, 230, 250),  # Лавандовий (ближні хмари)
                0.8, screen_height // 2
            )
        ]
    
    def update(self, delta_x):
        """
        Оновлення всіх шарів.
        
        Args:
            delta_x: float - Зміна позиції X
        """
        for layer in self.layers:
            layer.update(delta_x)
    
    def draw(self, screen):
        """
        Малювання всіх шарів.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        for layer in self.layers:
            layer.draw(screen)

