"""
@file: powerups.py
@description: Система power-ups (бонусів) для гри (щит, повільний час, подвійні очки, монети).
@dependencies: pygame, random
@created: 2024-12-19
"""

import math
import pygame
import random
import sys
import os

# Додаємо батьківську директорію до шляху для імпортів
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game_config import GameConfig

class PowerUp:
    """Базовий клас power-up."""
    
    def __init__(self, x, y, powerup_type, config):
        """
        Ініціалізація power-up.
        
        Args:
            x: float - Координата X
            y: float - Координата Y
            powerup_type: str - Тип power-up ('shield', 'slow_time', 'double_score', 'coin')
            config: GameConfig - Конфігурація гри
        """
        self.config = config
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = 30
        self.height = 30
        self.animation_time = 0
        
        # Кольори для різних типів
        self.colors = {
            'shield': (100, 150, 255),  # Синій
            'slow_time': (150, 100, 255),  # Фіолетовий
            'double_score': (255, 200, 100),  # Помаранчевий
            'coin': (255, 215, 0),  # Золотий
            'ghost': (200, 200, 255)  # Привид - прохід крізь труби
        }
    
    def update(self, speed=None):
        """Оновлення power-up. speed - фактична швидкість (з урахуванням slow_time)."""
        actual_speed = speed if speed is not None else self.config.PIPE_SPEED
        self.x -= actual_speed
        self.animation_time += 1
    
    def get_rect(self):
        """Отримати прямокутник колізії."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """
        Малювання power-up.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        color = self.colors.get(self.type, (255, 255, 255))
        
        # Анімація пульсації
        pulse = int(5 * abs(math.sin(self.animation_time * 0.2)))
        size = self.width + pulse
        
        # Малювання з центром
        rect = pygame.Rect(
            self.x + (self.width - size) // 2,
            self.y + (self.height - size) // 2,
            size, size
        )
        
        pygame.draw.ellipse(screen, color, rect)
        pygame.draw.ellipse(screen, (255, 255, 255), rect, 2)
        
        # Текстове позначення залежно від типу (без emojis)
        font = pygame.font.Font(None, 24)
        symbols = {
            'shield': 'S',
            'slow_time': 'T',
            'double_score': 'x2',
            'coin': 'C',
            'ghost': 'G'
        }
        symbol = symbols.get(self.type, '?')
        text = font.render(symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

class PowerUpManager:
    """Менеджер power-ups."""
    
    def __init__(self, config):
        """
        Ініціалізація менеджера power-ups.
        
        Args:
            config: GameConfig - Конфігурація гри
        """
        self.config = config
        self.powerups = []
        self.last_spawn_time = 0
        self.spawn_chance = 0.15  # 15% шанс появи power-up замість труби
        
        # Активні power-ups (ефекти)
        self.active_effects = {
            'shield': {'active': False, 'duration': 0},
            'slow_time': {'active': False, 'duration': 0},
            'double_score': {'active': False, 'duration': 0},
            'ghost': {'active': False, 'duration': 0, 'max_duration': 90}
        }
    
    def spawn_powerup(self, x, y):
        """
        Створення випадкового power-up.
        
        Args:
            x: float - Координата X
            y: float - Координата Y
        """
        types = ['shield', 'slow_time', 'double_score', 'coin', 'ghost']
        powerup_type = random.choice(types)
        
        powerup = PowerUp(x, y, powerup_type, self.config)
        self.powerups.append(powerup)
    
    def update(self, current_time, speed=None):
        """Оновлення power-ups та ефектів. speed - фактична швидкість (з урахуванням slow_time)."""
        actual_speed = speed if speed is not None else self.config.PIPE_SPEED
        # Оновлення power-ups
        for powerup in self.powerups[:]:
            powerup.update(actual_speed)
            if powerup.x + powerup.width < 0:
                self.powerups.remove(powerup)
        
        # Оновлення ефектів
        for effect in self.active_effects.values():
            if effect['active']:
                effect['duration'] -= 1
                if effect['duration'] <= 0:
                    effect['active'] = False
    
    def check_collision(self, bird):
        """
        Перевірка колізій з птахом.
        
        Args:
            bird: Bird - Об'єкт птаха
            
        Returns:
            list: Список зібраних power-ups
        """
        if bird is None:
            return []
        
        collected = []
        bird_rect = bird.get_rect()
        
        for powerup in self.powerups[:]:
            if bird_rect.colliderect(powerup.get_rect()):
                collected.append(powerup.type)
                
                # Активація ефектів
                if powerup.type == 'shield':
                    self.activate_shield()
                elif powerup.type == 'slow_time':
                    self.activate_slow_time()
                elif powerup.type == 'double_score':
                    self.activate_double_score()
                elif powerup.type == 'ghost':
                    self.activate_ghost()
                
                self.powerups.remove(powerup)
        
        return collected
    
    def activate_shield(self):
        """Активація щита (захист від однієї колізії)."""
        self.active_effects['shield']['active'] = True
        self.active_effects['shield']['duration'] = 600  # 10 секунд при 60 FPS
    
    def activate_slow_time(self):
        """Активація повільного часу."""
        self.active_effects['slow_time']['active'] = True
        self.active_effects['slow_time']['duration'] = 300  # 5 секунд
    
    def activate_double_score(self):
        """Активація подвійних очок."""
        self.active_effects['double_score']['active'] = True
        self.active_effects['double_score']['duration'] = 600  # 10 секунд
    
    def has_shield(self):
        """Перевірка, чи активний щит."""
        return self.active_effects['shield']['active']
    
    def use_shield(self):
        """Використання щита (при зіткненні)."""
        if self.active_effects['shield']['active']:
            self.active_effects['shield']['active'] = False
            self.active_effects['shield']['duration'] = 0
            return True
        return False
    
    def is_slow_time_active(self):
        """Перевірка, чи активний повільний час."""
        return self.active_effects['slow_time']['active']
    
    def is_double_score_active(self):
        """Перевірка, чи активні подвійні очки."""
        return self.active_effects['double_score']['active']
    
    def activate_ghost(self):
        """Активація режиму привида (прохід крізь труби)."""
        self.active_effects['ghost']['active'] = True
        self.active_effects['ghost']['duration'] = 90
        self.active_effects['ghost']['max_duration'] = 90
    
    def is_ghost_active(self):
        """Перевірка, чи активний ghost."""
        return self.active_effects['ghost']['active']
    
    def get_speed_multiplier(self):
        """Отримати множник швидкості (для повільного часу)."""
        return 0.5 if self.is_slow_time_active() else 1.0
    
    def draw(self, screen):
        """
        Малювання power-ups.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        for powerup in self.powerups:
            powerup.draw(screen)
        
        # Відображення активних ефектів
        y_offset = 10
        font = pygame.font.Font(None, 24)
        
        if self.active_effects['shield']['active']:
            text = font.render("[S] SHIELD", True, (100, 150, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 30
        
        if self.active_effects['slow_time']['active']:
            text = font.render("[T] SLOW TIME", True, (150, 100, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 30
        
        if self.active_effects['double_score']['active']:
            text = font.render("[x2] DOUBLE SCORE", True, (255, 200, 100))
            screen.blit(text, (10, y_offset))
            y_offset += 30
        if self.active_effects['ghost']['active']:
            text = font.render("[G] GHOST", True, (200, 200, 255))
            screen.blit(text, (10, y_offset))

