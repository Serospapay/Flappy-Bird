"""
@file: hud_elements.py
@description: HUD елементи для відображення інформації під час гри (power-ups, combo, тощо).
@dependencies: pygame, ui_elements
@created: 2024-12-19
"""

import pygame

from ui.ui_elements import Panel, Text
from ui.theme import HUD_PANEL_BG, BORDER_COLOR, BORDER_WIDTH, TEXT_MUTED

class PowerUpIndicator:
    """Індикатор активного power-up з таймером."""
    
    # Кольори для різних типів power-ups
    COLORS = {
        'shield': ((100, 200, 255), (50, 150, 255)),
        'slow_time': ((255, 200, 100), (255, 150, 50)),
        'double_score': ((255, 255, 100), (255, 200, 50)),
        'ghost': ((200, 200, 255), (150, 150, 220))
    }
    
    # Текстові позначення для power-ups (без emojis)
    SYMBOLS = {
        'shield': 'S',
        'slow_time': 'T',
        'double_score': 'x2',
        'coin': 'C',
        'ghost': 'G'
    }
    
    def __init__(self, powerup_type, duration, max_duration, x, y, font):
        """
        Ініціалізація індикатора.
        
        Args:
            powerup_type: str - Тип power-up
            duration: int - Поточна тривалість (в кадрах)
            max_duration: int - Максимальна тривалість
            x: int - Позиція X
            y: int - Позиція Y
            font: pygame.font.Font - Шрифт
        """
        self.type = powerup_type
        self.duration = duration
        self.max_duration = max_duration
        self.x = x
        self.y = y
        self.font = font
        
        self.colors = self.COLORS.get(powerup_type, ((200, 200, 200), (150, 150, 150)))
        
    def update(self, duration):
        """Оновлення тривалості."""
        self.duration = duration
        
    def draw(self, screen):
        """Малювання індикатора."""
        # Розрахунок прогресу (0.0 - 1.0)
        progress = max(0, min(1, self.duration / max(1, self.max_duration)))
        
        # Кешування шрифту (не створювати кожен кадр)
        if not hasattr(self, '_symbol_font'):
            self._symbol_font = pygame.font.Font(None, 28)
        if not hasattr(self, '_timer_font'):
            self._timer_font = pygame.font.Font(None, 16)
        
        panel_width = 50
        panel_height = 45
        panel = Panel(
            self.x - panel_width // 2, self.y - panel_height // 2,
            panel_width, panel_height,
            bg_color=HUD_PANEL_BG, alpha=140,
            border_color=self.colors[0], border_width=BORDER_WIDTH, shadow=False
        )
        panel.draw(screen)
        
        # Символ power-up (більший, бо панель менша)
        symbol_text = Text(
            self.SYMBOLS.get(self.type, '?'), 
            self._symbol_font,
            color=self.colors[0],
            shadow=True
        )
        symbol_text.draw(screen, (self.x, self.y - 8), center=True)
        
        # Компактний progress bar (горизонтальна лінія)
        bar_width = 40
        bar_height = 3
        bar_x = self.x - bar_width // 2
        bar_y = self.y + 12
        
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Заповнення progress bar
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(screen, self.colors[0], 
                            (bar_x, bar_y, fill_width, bar_height))
        
        seconds = max(0, int(self.duration / 60))
        Text(f"{seconds}", self._timer_font, color=TEXT_MUTED, shadow=True).draw(
            screen, (self.x, self.y + 18), center=True)


class ComboCounter:
    """Счетчик комбінацій (серій)."""
    
    def __init__(self, x, y, font):
        """
        Ініціалізація счетчика комбінацій.
        
        Args:
            x: int - Позиція X
            y: int - Позиція Y
            font: pygame.font.Font - Шрифт
        """
        self.x = x
        self.y = y
        self.font = font
        self.combo = 0
        self.max_combo = 0
        self.combo_timeout = 0
        self.max_timeout = 180  # 3 секунди при 60 FPS
        self.show_minimum = True  # Показувати тільки коли combo >= 5
        
    def add_combo(self, value=1):
        """Додати до комбінації."""
        self.combo += value
        self.max_combo = max(self.max_combo, self.combo)
        self.combo_timeout = self.max_timeout
        
    def reset_combo(self):
        """Скинути комбінацію."""
        self.combo = 0
        
    def update(self):
        """Оновлення таймера комбінації."""
        if self.combo > 0:
            self.combo_timeout -= 1
            if self.combo_timeout <= 0:
                self.reset_combo()
                
    def get_combo_bonus(self):
        """
        Отримати бонус від комбінації.
        
        Returns:
            int: Бонусний рахунок (0 якщо немає комбінації)
        """
        if self.combo >= 5:
            return (self.combo - 4)  # +1 за кожну комбінацію після 5
        return 0
        
    def draw(self, screen):
        """Малювання счетчика комбінацій."""
        if self.show_minimum and self.combo < 5:
            return  # Не показуємо якщо комбінація менше 5 (мінімалістичний режим)
        elif not self.show_minimum and self.combo < 2:
            return  # Звичайний режим - показуємо від 2
            
        # Розрахунок інтенсивності (більша комбінація = більша інтенсивність)
        intensity = min(1.0, self.combo / 10.0)
        
        # Колір залежить від комбінації
        if self.combo >= 10:
            color = (255, 50, 50)  # Червоний для великої комбінації
        elif self.combo >= 7:
            color = (255, 150, 50)  # Помаранчевий
        else:
            color = (255, 255, 100)  # Жовтий
            
        panel_width = 120
        panel_height = 35
        panel = Panel(
            self.x - panel_width // 2, self.y - panel_height // 2,
            panel_width, panel_height,
            bg_color=HUD_PANEL_BG, alpha=150,
            border_color=color, border_width=BORDER_WIDTH, shadow=False
        )
        panel.draw(screen)
        
        # Кешування шрифту для ComboCounter
        if not hasattr(self, '_combo_font'):
            self._combo_font = pygame.font.Font(None, 28)
        Text(f"x{self.combo}", self._combo_font, color=color, shadow=True, outline=False).draw(
            screen, (self.x, self.y), center=True)


class DifficultyIndicator:
    """Індикатор рівня складності."""
    
    def __init__(self, x, y, width, height, font):
        """
        Ініціалізація індикатора складності.
        
        Args:
            x: int - Позиція X
            y: int - Позиція Y
            width: int - Ширина
            height: int - Висота
            font: pygame.font.Font - Шрифт
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.difficulty_level = 0.0  # 0.0 - 1.0
        self.show = False  # За замовчуванням прихований
        
    def update(self, difficulty_level):
        """
        Оновлення рівня складності.
        
        Args:
            difficulty_level: float - Рівень складності (0.0 - 1.0)
        """
        self.difficulty_level = max(0.0, min(1.0, difficulty_level))
        
    def draw(self, screen):
        """Малювання індикатора складності."""
        if not self.show:
            return  # Прихований за замовчуванням для мінімального відволікання
        
        # Компактний індикатор - тільки маленька лінія внизу екрану
        bar_x = 0
        bar_y = screen.get_height() - 3
        bar_width = screen.get_width()
        bar_height = 3
        
        # Фон progress bar (дуже прозорий)
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Заповнення одним rect (оптимізація замість pixel-by-pixel)
        fill_width = int(bar_width * self.difficulty_level)
        if fill_width > 0:
            r = int(50 + self.difficulty_level * 205)
            g = int(200 - self.difficulty_level * 150)
            b = 50
            pygame.draw.rect(screen, (r, g, b), (bar_x, bar_y, fill_width, bar_height))

