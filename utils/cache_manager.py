"""
@file: cache_manager.py
@description: Менеджер кешування поверхонь для оптимізації рендерингу (зменшення повторних обчислень).
@dependencies: pygame
@created: 2024-12-19
"""

import pygame

class CacheManager:
    """Менеджер кешування поверхонь для оптимізації."""
    
    def __init__(self):
        """Ініціалізація менеджера кешу."""
        # Кеш для панелей (ключ: (width, height, bg_color, alpha, border_color, border_width))
        self.panel_cache = {}
        
        # Кеш для текстів (ключ: (text, font_size, color, outline_color, outline_width))
        self.text_cache = {}
        
        # Кеш для градієнтів (ключ: (width, height, color_from, color_to))
        self.gradient_cache = {}
        
        # Максимальний розмір кешу (щоб не витрачати занадто багато пам'яті)
        self.max_cache_size = 100
    
    def get_panel_surface(self, width, height, bg_color, alpha, border_color, border_width):
        """
        Отримати закешовану поверхню панелі або створити нову.
        
        Args:
            width: int - Ширина
            height: int - Висота
            bg_color: tuple - Колір фону
            alpha: int - Прозорість
            border_color: tuple - Колір межі
            border_width: int - Товщина межі
            
        Returns:
            pygame.Surface - Поверхня панелі
        """
        cache_key = (width, height, bg_color, alpha, border_color, border_width)
        
        if cache_key in self.panel_cache:
            return self.panel_cache[cache_key]
        
        # Створення нової поверхні
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Градієнт фону
        for y in range(height):
            ratio = y / max(1, height)
            r = int(bg_color[0] * (1 + ratio * 0.3))
            g = int(bg_color[1] * (1 + ratio * 0.3))
            b = int(bg_color[2] * (1 + ratio * 0.3))
            r = min(255, r)
            g = min(255, g)
            b = min(255, b)
            pygame.draw.line(panel_surface, (r, g, b, alpha), (0, y), (width, y))
        
        # Межа
        pygame.draw.rect(panel_surface, border_color, 
                        (0, 0, width, height), border_width)
        
        # Кешування
        if len(self.panel_cache) < self.max_cache_size:
            self.panel_cache[cache_key] = panel_surface
        
        return panel_surface
    
    def get_gradient_surface(self, width, height, color_from, color_to):
        """
        Отримати закешовану градієнтну поверхню або створити нову.
        
        Args:
            width: int - Ширина
            height: int - Висота
            color_from: tuple - Початковий колір
            color_to: tuple - Кінцевий колір
            
        Returns:
            pygame.Surface - Градієнтна поверхня
        """
        cache_key = (width, height, color_from, color_to)
        
        if cache_key in self.gradient_cache:
            return self.gradient_cache[cache_key]
        
        # Створення нової градієнтної поверхні
        gradient_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for y in range(height):
            ratio = y / max(1, height)
            r = int(color_from[0] * (1 - ratio) + color_to[0] * ratio)
            g = int(color_from[1] * (1 - ratio) + color_to[1] * ratio)
            b = int(color_from[2] * (1 - ratio) + color_to[2] * ratio)
            pygame.draw.line(gradient_surface, (r, g, b), (0, y), (width, y))
        
        # Кешування
        if len(self.gradient_cache) < self.max_cache_size:
            self.gradient_cache[cache_key] = gradient_surface
        
        return gradient_surface
    
    def clear_cache(self):
        """Очистити всі кеші."""
        self.panel_cache.clear()
        self.gradient_cache.clear()
        self.text_cache.clear()
    
    def get_cache_size(self):
        """Отримати поточний розмір кешу."""
        return len(self.panel_cache) + len(self.gradient_cache) + len(self.text_cache)

