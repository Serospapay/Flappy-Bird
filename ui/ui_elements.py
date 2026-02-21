"""
@file: ui_elements.py
@description: UI елементи для гри (кнопки, тексти, панелі) з покращеною стилізацією.
@dependencies: pygame
@created: 2024-12-19
"""

import pygame

try:
    from ui.theme import SHADOW_COLOR, SHADOW_OFFSET, BORDER_RADIUS
except ImportError:
    SHADOW_COLOR = (17, 17, 17)
    SHADOW_OFFSET = (2, 2)
    BORDER_RADIUS = 10

# Глобальний менеджер кешу (створюється при першому використанні)
_cache_manager = None

def get_cache_manager():
    """Отримати глобальний менеджер кешу."""
    global _cache_manager
    if _cache_manager is None:
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from utils.cache_manager import CacheManager
            _cache_manager = CacheManager()
        except ImportError:
            _cache_manager = None
    return _cache_manager

class Button:
    """Стилізована кнопка з hover ефектами та заокругленими кутами."""
    
    def __init__(self, x, y, width, height, text, font, callback=None,
                 bg_color=(100, 150, 200), hover_color=(150, 200, 255),
                 text_color=(255, 255, 255), border_color=None,
                 border_width=0, shadow=True, border_radius=10, hover_scale=1.0):
        """
        Ініціалізація кнопки.
        
        Args:
            x: int - Координата X (центр)
            y: int - Координата Y (центр)
            width: int - Ширина
            height: int - Висота
            text: str - Текст кнопки
            font: pygame.font.Font - Шрифт
            callback: function - Функція виклику при натисканні
            bg_color: tuple - Колір фону
            hover_color: tuple - Колір при наведенні (світліший)
            text_color: tuple - Колір тексту
            border_color: tuple | None - Колір межі (None = без обводки)
            border_width: int - Товщина межі (0 = без обводки)
            shadow: bool - Чи показувати тінь
            border_radius: int - Радіус заокруглення кутів (pygame-ce)
            hover_scale: float - Масштаб при наведенні (1.0 = без збільшення)
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
        self.border_radius = min(border_radius, width // 2, height // 2)
        self.hover_scale = hover_scale
        
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
        Малювання кнопки з заокругленими кутами та hover ефектом.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        # Hover: невелике збільшення (якщо hover_scale > 1.0)
        scale = self.hover_scale if self.hovered else 1.0
        w = int(self.rect.width * scale)
        h = int(self.rect.height * scale)
        cx, cy = self.rect.center
        draw_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        rad = min(self.border_radius, w // 2, h // 2)
        
        # Тінь
        if self.shadow:
            shadow_rect = draw_rect.move(2, 2)
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 80),
                            (0, 0, shadow_rect.width, shadow_rect.height),
                            border_radius=rad)
            screen.blit(shadow_surf, shadow_rect)
        
        # Колір (світліший при hover)
        color = self.hover_color if self.hovered else self.bg_color
        
        # Фон з заокругленими кутами
        pygame.draw.rect(screen, color, draw_rect, border_radius=rad)
        
        # Тонка обводка лише якщо задана
        if self.border_width > 0 and self.border_color:
            pygame.draw.rect(screen, self.border_color, draw_rect,
                             width=self.border_width, border_radius=rad)
        
        # Текст: малюємо рівно двічі — тінь, потім основний
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        shadow_surf = self.font.render(self.text, True, SHADOW_COLOR)
        screen.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surface, (text_rect.x, text_rect.y))

class Text:
    """Стилізований текст з єдиною тінню (shadow_color #111111, offset +2)."""
    
    def __init__(self, text, font, color=(255, 255, 255),
                 shadow=True, shadow_color=None, shadow_offset=None,
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
        self.shadow_color = shadow_color if shadow_color is not None else SHADOW_COLOR
        self.shadow_offset = shadow_offset if shadow_offset is not None else SHADOW_OFFSET
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
        
        # Тінь: малюємо рівно двічі (як у Button)
        if self.shadow and not self.outline:
            shadow_surf = self.font.render(self.text, True, self.shadow_color)
            sx = rect.x + self.shadow_offset[0]
            sy = rect.y + self.shadow_offset[1]
            screen.blit(shadow_surf, (sx, sy))
        screen.blit(surface, rect)

class Panel:
    """Стилізована панель з заокругленими кутами (border_radius)."""
    
    def __init__(self, x, y, width, height,
                 bg_color=(30, 40, 60), alpha=200,
                 border_color=(100, 130, 170), border_width=1,
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
        Малювання панелі з використанням кешування.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        rad = min(self.corner_radius, self.rect.width // 2, self.rect.height // 2)
        if self.shadow:
            shadow_rect = self.rect.move(2, 2)
            shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (0, 0, self.rect.width, self.rect.height), border_radius=rad)
            screen.blit(shadow_surf, shadow_rect)
        
        cache = get_cache_manager()
        if cache:
            panel_surface = cache.get_panel_surface(
                self.rect.width, self.rect.height,
                self.bg_color, self.alpha,
                self.border_color, self.border_width,
                border_radius=rad
            )
        else:
            panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            fill_color = (*self.bg_color, self.alpha)
            pygame.draw.rect(panel_surface, fill_color, (0, 0, self.rect.width, self.rect.height), border_radius=rad)
            if self.border_width > 0:
                pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.rect.width, self.rect.height),
                                 width=self.border_width, border_radius=rad)
        
        screen.blit(panel_surface, self.rect)

