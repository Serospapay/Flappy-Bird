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
    
    THEMES = {
        "light": [
            ((135, 206, 250), 0.1),  # Небесно-блакитний
            ((173, 216, 230), 0.3),
            ((176, 224, 230), 0.5),
            ((230, 230, 250), 0.8),
        ],
        "dark": [
            ((25, 35, 55), 0.1),   # Темно-синій
            ((35, 50, 80), 0.3),
            ((45, 65, 95), 0.5),
            ((60, 80, 110), 0.8),
        ],
    }
    
    def __init__(self, screen_width, screen_height, theme="light"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.theme = theme
        self._build_layers()
    
    def _build_layers(self):
        colors = ParallaxBackground.THEMES.get(self.theme, ParallaxBackground.THEMES["light"])
        sw, sh = self.screen_width, self.screen_height
        c1, s1 = colors[0]
        c2, s2 = colors[1]
        c3, s3 = colors[2]
        c4, s4 = colors[3]
        self.layers = [
            ParallaxLayer(sw, sh, c1, s1, 0),
            ParallaxLayer(sw, sh // 2, c2, s2, 0),
            ParallaxLayer(sw, sh // 3, c3, s3, sh // 4),
            ParallaxLayer(sw, sh // 4, c4, s4, sh // 2),
        ]
    
    def update(self, delta_x):
        """
        Оновлення всіх шарів.
        
        Args:
            delta_x: float - Зміна позиції X
        """
        for layer in self.layers:
            layer.update(delta_x)
    
    def set_theme(self, theme):
        """Зміна теми (light/dark)."""
        if theme != self.theme:
            self.theme = theme
            self._build_layers()
    
    def draw(self, screen):
        """Малювання всіх шарів."""
        for layer in self.layers:
            layer.draw(screen)

