"""
@file: slider.py
@description: Візуальний слайдер (slider) для налаштувань.
@dependencies: pygame, ui_elements
@created: 2024-12-19
"""

import pygame
import sys
import os

# Додаємо батьківську директорію до шляху для імпортів
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.ui_elements import Panel, Text
from ui.theme import PANEL_DARK, BORDER_COLOR, BORDER_WIDTH, ACCENT_PRIMARY, ACCENT_HOVER, TEXT_MUTED

class Slider:
    """Візуальний слайдер для вибору значення."""
    
    def __init__(self, x, y, width, height, min_value, max_value, value, 
                 font, label="", callback=None):
        """
        Ініціалізація слайдера.
        
        Args:
            x: int - Позиція X
            y: int - Позиція Y
            width: int - Ширина
            height: int - Висота
            min_value: float - Мінімальне значення
            max_value: float - Максимальне значення
            value: float - Поточне значення
            font: pygame.font.Font - Шрифт
            label: str - Підпис слайдера
            callback: function - Функція виклику при зміні (value)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = max(min_value, min(max_value, value))
        self.font = font
        self.label = label
        self.callback = callback
        
        self.dragging = False
        self.hovered = False
        
        self.track_color = (60, 70, 90)
        self.fill_color = ACCENT_PRIMARY
        self.handle_color = ACCENT_HOVER
        self.handle_hover_color = (200, 230, 255)
        
    def get_ratio(self):
        """Отримати співвідношення значення (0.0 - 1.0)."""
        if self.max_value == self.min_value:
            return 0.0
        return (self.value - self.min_value) / (self.max_value - self.min_value)
    
    def set_value_from_pos(self, x):
        """
        Встановити значення з позиції X.
        
        Args:
            x: int - Позиція X миші
        """
        # Перевірка меж
        track_start = self.rect.x + 15
        track_end = self.rect.right - 15
        track_width = track_end - track_start
        
        if track_width <= 0:
            return
        
        # Нормалізація позиції
        rel_x = max(0, min(track_width, x - track_start))
        ratio = rel_x / track_width
        
        # Оновлення значення
        old_value = self.value
        self.value = self.min_value + ratio * (self.max_value - self.min_value)
        
        # Виклик callback якщо значення змінилось
        if old_value != self.value and self.callback:
            self.callback(self.value)
    
    def update(self, mouse_pos, mouse_pressed):
        """
        Оновлення стану слайдера.
        
        Args:
            mouse_pos: tuple - Позиція миші
            mouse_pressed: bool - Чи натиснута миша
        """
        handle_rect = self.get_handle_rect()
        self.hovered = handle_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos)
        
        if mouse_pressed:
            if handle_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.set_value_from_pos(mouse_pos[0])
        else:
            self.dragging = False
    
    def get_handle_rect(self):
        """Отримати прямокутник для ручки слайдера."""
        ratio = self.get_ratio()
        track_start = self.rect.x + 15
        track_end = self.rect.right - 15
        track_width = track_end - track_start
        handle_x = track_start + ratio * track_width - 10
        
        return pygame.Rect(handle_x, self.rect.centery - 12, 20, 24)
    
    def draw(self, screen):
        """
        Малювання слайдера.
        
        Args:
            screen: pygame.Surface - Екран
        """
        if self.label:
            Text(self.label, self.font, color=TEXT_MUTED, shadow=True).draw(
                screen, (self.rect.centerx, self.rect.y - 25), center=True)
        
        panel = Panel(
            self.rect.x, self.rect.y, self.rect.width, self.rect.height,
            bg_color=PANEL_DARK, alpha=200,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=False
        )
        panel.draw(screen)
        
        # Трек (доріжка)
        track_start = self.rect.x + 15
        track_end = self.rect.right - 15
        track_y = self.rect.centery
        track_height = 8
        
        # Фон треку
        pygame.draw.rect(screen, self.track_color,
                        (track_start, track_y - track_height // 2,
                         track_end - track_start, track_height))
        
        # Заповнення треку
        ratio = self.get_ratio()
        fill_width = int((track_end - track_start) * ratio)
        if fill_width > 0:
            pygame.draw.rect(screen, self.fill_color,
                            (track_start, track_y - track_height // 2,
                             fill_width, track_height))
        
        # Ручка (handle)
        handle_rect = self.get_handle_rect()
        handle_color = self.handle_hover_color if (self.hovered or self.dragging) else self.handle_color
        
        # Тінь ручки
        shadow_rect = handle_rect.move(2, 2)
        shadow_surface = pygame.Surface((handle_rect.width, handle_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 100))
        screen.blit(shadow_surface, shadow_rect)
        
        pygame.draw.rect(screen, handle_color, handle_rect, border_radius=10)
        
        Text(f"{int(self.value * 100)}%", pygame.font.Font(None, 24),
             color=(255, 255, 255), shadow=True).draw(
            screen, (self.rect.right - 60, self.rect.centery), center=True)


