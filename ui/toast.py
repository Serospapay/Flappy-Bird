"""
@file: toast.py
@description: Система спливаючих повідомлень (Toast notifications) для гри.
@dependencies: pygame, ui_elements
@created: 2024-12-19
"""

import pygame

from ui.ui_elements import Panel, Text

class Toast:
    """Одне спливаюче повідомлення."""
    
    TYPES = {
        'achievement': ((255, 215, 0), '[+]'),  # Золотий
        'record': ((255, 255, 100), '[*]'),  # Жовтий
        'combo': ((255, 100, 100), '[!]'),  # Червоний
        'info': ((100, 200, 255), '[i]'),  # Блакитний
        'success': ((100, 255, 100), '[OK]'),  # Зелений
        'warning': ((255, 150, 50), '[-]')  # Помаранчевий
    }
    
    def __init__(self, message, toast_type='info', duration=120):
        """
        Ініціалізація Toast.
        
        Args:
            message: str - Текст повідомлення
            toast_type: str - Тип повідомлення ('achievement', 'record', 'combo', 'info', 'success', 'warning')
            duration: int - Тривалість в кадрах (зменшено для меншого відволікання)
        """
        self.message = message
        self.type = toast_type
        self.duration = duration
        self.max_duration = duration
        self.alpha = 0
        self.target_alpha = 200  # Менша прозорість
        self.y_offset = 0
        self.target_y_offset = 0
        
        self.color = self.TYPES.get(toast_type, ((200, 200, 200), '·'))[0]
        self.symbol = self.TYPES.get(toast_type, ((200, 200, 200), '·'))[1]
        
    def update(self):
        """Оновлення Toast."""
        self.duration -= 1
        
        # Поява (fade in) - швидше
        if self.max_duration - self.duration < 15:
            progress = (15 - (self.max_duration - self.duration)) / 15
            self.alpha = int(self.target_alpha * (1 - progress))
            self.y_offset = int(20 * progress)  # Менше зміщення
        # Затухання (fade out) - швидше
        elif self.duration < 15:
            progress = self.duration / 15
            self.alpha = int(self.target_alpha * progress)
            self.y_offset = int(20 * (1 - progress))
        else:
            self.alpha = self.target_alpha
            self.y_offset = 0
            
        return self.duration > 0
        
    def draw(self, screen, x, y, font):
        """
        Малювання Toast.
        
        Args:
            screen: pygame.Surface - Екран
            x: int - Позиція X
            y: int - Позиція Y
            font: pygame.font.Font - Шрифт
        """
        if self.alpha <= 0:
            return
            
        # Розрахунок розміру панелі (компактніше)
        text_surface = font.render(f"{self.symbol} {self.message}", True, (255, 255, 255))
        padding = 12  # Менший padding
        panel_width = text_surface.get_width() + padding * 2
        panel_height = text_surface.get_height() + padding * 2
        
        # Створення поверхні з прозорістю
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Фон панелі
        bg_color = (*self.color, int(self.alpha * 0.9))
        pygame.draw.rect(panel_surface, bg_color, 
                        (0, 0, panel_width, panel_height), border_radius=10)
        
        # Межа
        border_color = (*self.color, self.alpha)
        pygame.draw.rect(panel_surface, border_color,
                        (0, 0, panel_width, panel_height), width=2, border_radius=10)
        
        # Текст
        text_with_alpha = font.render(f"{self.symbol} {self.message}", True, (255, 255, 255))
        text_with_alpha.set_alpha(self.alpha)
        panel_surface.blit(text_with_alpha, (padding, padding))
        
        # Малювання на екрані
        screen.blit(panel_surface, (x - panel_width // 2, y + self.y_offset - panel_height // 2))


class ToastSystem:
    """Система керування Toast повідомленнями."""
    
    def __init__(self, screen_width):
        """
        Ініціалізація системи Toast.
        
        Args:
            screen_width: int - Ширина екрану
        """
        self.screen_width = screen_width
        self.toasts = []
        self.positions = []  # Позиції для кожного Toast
        
    def add_toast(self, message, toast_type='info', duration=180):
        """
        Додати нове Toast повідомлення.
        
        Args:
            message: str - Текст повідомлення
            toast_type: str - Тип повідомлення
            duration: int - Тривалість в кадрах
        """
        toast = Toast(message, toast_type, duration)
        self.toasts.append(toast)
        
        # Розподіл позицій по вертикалі
        self._update_positions()
        
    def _update_positions(self):
        """Оновлення позицій Toast повідомлень (зверху для меншого відволікання)."""
        start_y = 80  # Вище на екрані
        spacing = 50  # Менший інтервал
        
        self.positions = []
        for i, toast in enumerate(self.toasts):
            self.positions.append((self.screen_width // 2, start_y + i * spacing))
        
    def update(self):
        """Оновлення всіх Toast."""
        self.toasts = [t for t in self.toasts if t.update()]
        self._update_positions()
        
    def draw(self, screen, font):
        """
        Малювання всіх Toast.
        
        Args:
            screen: pygame.Surface - Екран
            font: pygame.font.Font - Шрифт
        """
        for toast, pos in zip(self.toasts, self.positions):
            toast.draw(screen, pos[0], pos[1], font)

