"""
@file: ui_elements.py
@description: UI елементи для гри (кнопки, тексти, панелі) з покращеною стилізацією.
@dependencies: pygame, math
@created: 2024-12-19
"""

import pygame
import math

class Button:
    """Стилізована кнопка з hover ефектами."""
    
    def __init__(self, x, y, width, height, text, font, callback=None,
                 bg_color=(100, 150, 200), hover_color=(150, 200, 255),
                 text_color=(255, 255, 255), border_color=(255, 255, 255),
                 border_width=2, shadow=True):
        """
        Ініціалізація кнопки.
        
        Args:
            x: int - Координата X
            y: int - Координата Y
            width: int - Ширина
            height: int - Висота
            text: str - Текст кнопки
            font: pygame.font.Font - Шрифт
            callback: function - Функція виклику при натисканні
            bg_color: tuple - Колір фону
            hover_color: tuple - Колір при наведенні
            text_color: tuple - Колір тексту
            border_color: tuple - Колір межі
            border_width: int - Товщина межі
            shadow: bool - Чи показувати тінь
        """
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.shadow = shadow
        
        self.hovered = False
        self.clicked = False
        self.animation_time = 0
        
    def update(self, mouse_pos, mouse_clicked):
        """
        Оновлення стану кнопки.
        
        Args:
            mouse_pos: tuple - Позиція миші
            mouse_clicked: bool - Чи натиснута миша
        """
        self.animation_time += 0.1
        prev_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if mouse_clicked and self.hovered:
            if not self.clicked:
                self.clicked = True
                if self.callback:
                    self.callback()
        else:
            self.clicked = False
    
    def draw(self, screen):
        """
        Малювання кнопки.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        # Тінь
        if self.shadow:
            shadow_offset = 5
            shadow_rect = self.rect.move(shadow_offset, shadow_offset)
            shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 100))
            screen.blit(shadow_surface, shadow_rect)
        
        # Анімація hover
        scale = 1.0
        if self.hovered:
            scale = 1.05 + 0.02 * math.sin(self.animation_time * 10)
        else:
            scale = 1.0
        
        scaled_rect = pygame.Rect(
            self.rect.centerx - int(self.rect.width * scale / 2),
            self.rect.centery - int(self.rect.height * scale / 2),
            int(self.rect.width * scale),
            int(self.rect.height * scale)
        )
        
        # Вибір кольору
        color = self.hover_color if self.hovered else self.bg_color
        
        # Градієнт фону
        gradient_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        
        # Створення градієнту
        for y in range(scaled_rect.height):
            ratio = y / scaled_rect.height
            r = int(color[0] * (1 - ratio * 0.2))
            g = int(color[1] * (1 - ratio * 0.2))
            b = int(color[2] * (1 - ratio * 0.2))
            pygame.draw.line(gradient_surface, (r, g, b), (0, y), (scaled_rect.width, y))
        
        screen.blit(gradient_surface, scaled_rect)
        
        # Межа
        pygame.draw.rect(screen, self.border_color, scaled_rect, self.border_width)
        
        # Текст
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        
        # Тінь тексту
        shadow_text = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(shadow_text, text_rect.move(2, 2))
        screen.blit(text_surface, text_rect)

class Text:
    """Стилізований текст з тінню та обведенням."""
    
    def __init__(self, text, font, color=(255, 255, 255), 
                 shadow=True, shadow_color=(0, 0, 0), shadow_offset=(2, 2),
                 outline=False, outline_color=(0, 0, 0), outline_width=1):
        """
        Ініціалізація тексту.
        
        Args:
            text: str - Текст
            font: pygame.font.Font - Шрифт
            color: tuple - Колір тексту
            shadow: bool - Чи показувати тінь
            shadow_color: tuple - Колір тіні
            shadow_offset: tuple - Зміщення тіні
            outline: bool - Чи показувати обведення
            outline_color: tuple - Колір обведення
            outline_width: int - Товщина обведення
        """
        self.text = text
        self.font = font
        self.color = color
        self.shadow = shadow
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset
        self.outline = outline
        self.outline_color = outline_color
        self.outline_width = outline_width
    
    def render(self):
        """
        Створення поверхні з текстом.
        
        Returns:
            pygame.Surface - Поверхня з текстом
        """
        # Обведення
        if self.outline:
            # Малюємо текст з усіх сторін для обведення
            surfaces = []
            for dx in range(-self.outline_width, self.outline_width + 1):
                for dy in range(-self.outline_width, self.outline_width + 1):
                    if dx != 0 or dy != 0:
                        text_surf = self.font.render(self.text, True, self.outline_color)
                        surfaces.append((text_surf, (dx, dy)))
            
            # Основний текст
            main_text = self.font.render(self.text, True, self.color)
            
            # Створення поверхні
            text_rect = main_text.get_rect()
            surface = pygame.Surface(
                (text_rect.width + self.outline_width * 2,
                 text_rect.height + self.outline_width * 2),
                pygame.SRCALPHA
            )
            
            # Малювання обведення
            for surf, offset in surfaces:
                surface.blit(surf, (self.outline_width + offset[0], self.outline_width + offset[1]))
            
            # Малювання основного тексту
            surface.blit(main_text, (self.outline_width, self.outline_width))
            
            return surface
        else:
            return self.font.render(self.text, True, self.color)
    
    def draw(self, screen, position, center=False):
        """
        Малювання тексту.
        
        Args:
            screen: pygame.Surface - Екран
            position: tuple - Позиція (x, y)
            center: bool - Чи центрувати
        """
        surface = self.render()
        rect = surface.get_rect()
        
        if center:
            rect.center = position
        else:
            rect.topleft = position
        
        # Тінь
        if self.shadow and not self.outline:
            shadow_surf = self.font.render(self.text, True, self.shadow_color)
            shadow_rect = shadow_surf.get_rect()
            if center:
                shadow_rect.center = (position[0] + self.shadow_offset[0], 
                                     position[1] + self.shadow_offset[1])
            else:
                shadow_rect.topleft = (position[0] + self.shadow_offset[0],
                                      position[1] + self.shadow_offset[1])
            screen.blit(shadow_surf, shadow_rect)
        
        screen.blit(surface, rect)

class Panel:
    """Стилізована панель з градієнтом та тінню."""
    
    def __init__(self, x, y, width, height, 
                 bg_color=(50, 50, 80), alpha=200,
                 border_color=(150, 150, 200), border_width=2,
                 shadow=True, corner_radius=10):
        """
        Ініціалізація панелі.
        
        Args:
            x: int - Координата X
            y: int - Координата Y
            width: int - Ширина
            height: int - Висота
            bg_color: tuple - Колір фону
            alpha: int - Прозорість (0-255)
            border_color: tuple - Колір межі
            border_width: int - Товщина межі
            shadow: bool - Чи показувати тінь
            corner_radius: int - Радіус заокруглення кутів
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.alpha = alpha
        self.border_color = border_color
        self.border_width = border_width
        self.shadow = shadow
        self.corner_radius = corner_radius
        
    def draw(self, screen):
        """
        Малювання панелі.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        # Тінь
        if self.shadow:
            shadow_rect = self.rect.move(5, 5)
            shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 100))
            screen.blit(shadow_surface, shadow_rect)
        
        # Панель з градієнтом
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Градієнт фону
        for y in range(self.rect.height):
            ratio = y / self.rect.height
            r = int(self.bg_color[0] * (1 + ratio * 0.3))
            g = int(self.bg_color[1] * (1 + ratio * 0.3))
            b = int(self.bg_color[2] * (1 + ratio * 0.3))
            r = min(255, r)
            g = min(255, g)
            b = min(255, b)
            pygame.draw.line(panel_surface, (r, g, b, self.alpha), (0, y), (self.rect.width, y))
        
        # Межа
        pygame.draw.rect(panel_surface, self.border_color, 
                        (0, 0, self.rect.width, self.rect.height), 
                        self.border_width)
        
        screen.blit(panel_surface, self.rect)

