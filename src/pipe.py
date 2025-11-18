"""
@file: pipe.py
@description: Клас PipeManager для керування трубами (перешкодами). Генерація, рух та колізії.
@dependencies: pygame, game_config, random
@created: 2024-12-19
"""

import pygame
import random
import sys
import os

# Додаємо батьківську директорію до шляху для імпортів
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game_config import GameConfig

class Pipe:
    """Клас однієї труби."""
    
    TYPE_NORMAL = "normal"
    TYPE_MOVING = "moving"  # Рухома труба
    TYPE_SHRINKING = "shrinking"  # Труба що зменшується
    
    def __init__(self, x, gap_y, gap_size, config, pipe_type=TYPE_NORMAL):
        """
        Ініціалізація труби.
        
        Args:
            x: Позиція X
            gap_y: Позиція Y проміжку
            gap_size: Розмір проміжку
            config: Об'єкт GameConfig
            pipe_type: str - Тип труби (normal, moving, shrinking)
        """
        self.config = config
        self.x = x
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.width = config.PIPE_WIDTH
        self.passed = False
        self.type = pipe_type
        
        # Для рухомої труби
        self.move_direction = 1  # 1 - вниз, -1 - вгору
        self.move_speed = 1.5
        self.move_range = 150  # Діапазон руху
        
        # Для труби що зменшується
        self.shrink_speed = 0.3
        self.original_gap = gap_size
        
        # Верхня труба (гарантуємо int)
        self.top_height = int(gap_y)
        # Нижня труба (гарантуємо int)
        self.bottom_y = int(gap_y + gap_size)
        self.bottom_height = int(config.SCREEN_HEIGHT - self.bottom_y)
        
    def update(self):
        """Оновлення позиції труби."""
        self.x -= self.config.PIPE_SPEED
        
        # Рух для рухомої труби
        if self.type == Pipe.TYPE_MOVING:
            self.gap_y += self.move_direction * self.move_speed
            
            # Зміна напрямку
            if self.gap_y <= self.config.PIPE_HEAD_HEIGHT + 50:
                self.move_direction = 1
            elif self.gap_y >= self.config.SCREEN_HEIGHT - self.gap_size - self.config.PIPE_HEAD_HEIGHT - 50:
                self.move_direction = -1
            
            # Оновлення висоти (конвертація в int)
            self.top_height = int(self.gap_y)
            self.bottom_y = int(self.gap_y + self.gap_size)
            self.bottom_height = int(self.config.SCREEN_HEIGHT - self.bottom_y)
        
        # Зменшення для труби що зменшується
        elif self.type == Pipe.TYPE_SHRINKING:
            self.gap_size = max(self.original_gap * 0.5, self.gap_size - self.shrink_speed)
            self.bottom_y = int(self.gap_y + self.gap_size)
            self.bottom_height = int(self.config.SCREEN_HEIGHT - self.bottom_y)
        
    def get_rects(self):
        """Отримати прямокутники колізій (верхня та нижня труба + голови)."""
        rects = []
        
        # Верхня труба (конвертація в int)
        rects.append(pygame.Rect(self.x, 0, self.width, int(self.top_height)))
        # Голова верхньої труби (конвертація в int)
        top_height_int = int(self.top_height)
        rects.append(pygame.Rect(
            self.x - 5, 
            top_height_int - self.config.PIPE_HEAD_HEIGHT, 
            self.width + 10, 
            self.config.PIPE_HEAD_HEIGHT
        ))
        
        # Нижня труба (конвертація в int)
        bottom_y_int = int(self.bottom_y)
        bottom_height_int = int(self.bottom_height)
        rects.append(pygame.Rect(self.x, bottom_y_int, self.width, bottom_height_int))
        # Голова нижньої труби (конвертація в int)
        rects.append(pygame.Rect(
            self.x - 5, 
            bottom_y_int, 
            self.width + 10, 
            self.config.PIPE_HEAD_HEIGHT
        ))
        
        return rects
        
    def draw(self, screen):
        """
        Малювання труби з покращеною стилізацією.
        
        Args:
            screen: Екран pygame для малювання
        """
        # Вибір кольору в залежності від типу
        if self.type == Pipe.TYPE_MOVING:
            color = (100, 150, 255)  # Синій
            head_color = (50, 100, 200)  # Темно-синій
            dark_color = (30, 70, 150)  # Темніший
        elif self.type == Pipe.TYPE_SHRINKING:
            color = (255, 150, 100)  # Помаранчевий
            head_color = (200, 100, 50)  # Темно-помаранчевий
            dark_color = (180, 80, 30)  # Темніший
        else:
            color = self.config.PIPE_COLOR
            head_color = self.config.PIPE_HEAD_COLOR
            dark_color = (20, 80, 20)  # Темніший зелений
        
        # Тінь для верхньої труби (конвертація в int для безпеки)
        top_height_int = int(self.top_height)
        shadow_surface = pygame.Surface((self.width + 4, top_height_int + 4), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 60))
        screen.blit(shadow_surface, (self.x + 2, 2))
        
        # Верхня труба з градієнтом (конвертація в int)
        pipe_surface = pygame.Surface((self.width, top_height_int), pygame.SRCALPHA)
        for y in range(top_height_int):
            ratio = y / max(1, top_height_int)
            r = int(color[0] * (1 - ratio * 0.4))
            g = int(color[1] * (1 - ratio * 0.4))
            b = int(color[2] * (1 - ratio * 0.4))
            grad_color = (max(0, r), max(0, g), max(0, b))
            pygame.draw.line(pipe_surface, grad_color, (0, y), (self.width, y))
        
        # Текстура (вертикальні смуги)
        for i in range(0, self.width, 8):
            pygame.draw.line(pipe_surface, dark_color, (i, 0), (i, top_height_int), 1)
        
        screen.blit(pipe_surface, (self.x, 0))
        
        # Межа верхньої труби
        pygame.draw.rect(screen, dark_color, (self.x, 0, self.width, top_height_int), 2)
        
        # Голова верхньої труби з градієнтом
        head_y = top_height_int - self.config.PIPE_HEAD_HEIGHT
        head_surface = pygame.Surface((self.width + 10, self.config.PIPE_HEAD_HEIGHT), pygame.SRCALPHA)
        for y in range(self.config.PIPE_HEAD_HEIGHT):
            ratio = y / max(1, self.config.PIPE_HEAD_HEIGHT)
            r = int(head_color[0] * (1 - ratio * 0.3))
            g = int(head_color[1] * (1 - ratio * 0.3))
            b = int(head_color[2] * (1 - ratio * 0.3))
            grad_color = (max(0, r), max(0, g), max(0, b))
            pygame.draw.line(head_surface, grad_color, (0, y), (self.width + 10, y))
        
        # Відблиск на голові
        highlight_rect = pygame.Rect(2, 2, self.width + 6, self.config.PIPE_HEAD_HEIGHT // 3)
        highlight_color = tuple(min(255, c + 30) for c in head_color)
        pygame.draw.rect(head_surface, (*highlight_color, 150), highlight_rect)
        
        screen.blit(head_surface, (self.x - 5, head_y))
        pygame.draw.rect(screen, dark_color, 
                        (self.x - 5, head_y, self.width + 10, self.config.PIPE_HEAD_HEIGHT), 2)
        
        # Тінь для нижньої труби (конвертація в int)
        bottom_height_int = int(self.bottom_height)
        bottom_y_int = int(self.bottom_y)
        shadow_surface2 = pygame.Surface((self.width + 4, bottom_height_int + 4), pygame.SRCALPHA)
        shadow_surface2.fill((0, 0, 0, 60))
        screen.blit(shadow_surface2, (self.x + 2, bottom_y_int + 2))
        
        # Нижня труба з градієнтом
        bottom_surface = pygame.Surface((self.width, bottom_height_int), pygame.SRCALPHA)
        for y in range(bottom_height_int):
            ratio = y / max(1, bottom_height_int)
            r = int(color[0] * (1 + ratio * 0.3))
            g = int(color[1] * (1 + ratio * 0.3))
            b = int(color[2] * (1 + ratio * 0.3))
            grad_color = (min(255, r), min(255, g), min(255, b))
            pygame.draw.line(bottom_surface, grad_color, (0, y), (self.width, y))
        
        # Текстура (вертикальні смуги)
        for i in range(0, self.width, 8):
            pygame.draw.line(bottom_surface, dark_color, (i, 0), (i, bottom_height_int), 1)
        
        screen.blit(bottom_surface, (self.x, bottom_y_int))
        
        # Межа нижньої труби
        pygame.draw.rect(screen, dark_color, 
                        (self.x, bottom_y_int, self.width, bottom_height_int), 2)
        
        # Голова нижньої труби з градієнтом
        head_surface2 = pygame.Surface((self.width + 10, self.config.PIPE_HEAD_HEIGHT), pygame.SRCALPHA)
        for y in range(self.config.PIPE_HEAD_HEIGHT):
            ratio = y / max(1, self.config.PIPE_HEAD_HEIGHT)
            r = int(head_color[0] * (1 + ratio * 0.3))
            g = int(head_color[1] * (1 + ratio * 0.3))
            b = int(head_color[2] * (1 + ratio * 0.3))
            grad_color = (min(255, r), min(255, g), min(255, b))
            pygame.draw.line(head_surface2, grad_color, (0, y), (self.width + 10, y))
        
        # Відблиск на голові
        highlight_rect2 = pygame.Rect(2, 2, self.width + 6, self.config.PIPE_HEAD_HEIGHT // 3)
        highlight_color2 = tuple(min(255, c + 30) for c in head_color)
        pygame.draw.rect(head_surface2, (*highlight_color2, 150), highlight_rect2)
        
        screen.blit(head_surface2, (self.x - 5, bottom_y_int))
        pygame.draw.rect(screen, dark_color,
                        (self.x - 5, bottom_y_int, self.width + 10, self.config.PIPE_HEAD_HEIGHT), 2)


class PipeManager:
    """Менеджер для керування всіма трубами."""
    
    def __init__(self, config):
        """
        Ініціалізація менеджера труб.
        
        Args:
            config: Об'єкт GameConfig
        """
        self.config = config
        self.pipes = []
        self.last_spawn_time = 0
        self.score = 0
        
    def spawn_pipe(self, current_time, score=0):
        """Створення нової труби, якщо пройшов достатній час."""
        if current_time - self.last_spawn_time >= self.config.PIPE_SPAWN_INTERVAL:
            gap_y = random.randint(
                self.config.PIPE_HEAD_HEIGHT + 50,
                self.config.SCREEN_HEIGHT - self.config.PIPE_GAP - self.config.PIPE_HEAD_HEIGHT - 50
            )
            
            # Визначення типу труби в залежності від складності
            pipe_type = Pipe.TYPE_NORMAL
            if score > 10:
                # Після 10 очок з'являються рухомі труби
                if random.random() < 0.3:  # 30% шанс
                    pipe_type = Pipe.TYPE_MOVING
            if score > 25:
                # Після 25 очок з'являються труби що зменшуються
                if random.random() < 0.2:  # 20% шанс
                    pipe_type = Pipe.TYPE_SHRINKING
            
            new_pipe = Pipe(
                self.config.SCREEN_WIDTH,
                gap_y,
                self.config.PIPE_GAP,
                self.config,
                pipe_type
            )
            self.pipes.append(new_pipe)
            self.last_spawn_time = current_time
            
    def update(self, score=0):
        """Оновлення всіх труб."""
        current_time = pygame.time.get_ticks()
        self.spawn_pipe(current_time, score)
        
        # Оновлення труб
        for pipe in self.pipes[:]:
            pipe.update()
            
            # Видалення труб, що вийшли за межі екрану
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)
                
    def check_collision(self, bird):
        """
        Перевірка колізій птаха з трубами.
        
        Args:
            bird: Об'єкт Bird
            
        Returns:
            True якщо є колізія, False інакше
        """
        if bird is None:
            return False
            
        bird_rect = bird.get_rect()
        
        for pipe in self.pipes:
            pipe_rects = pipe.get_rects()
            for rect in pipe_rects:
                if bird_rect.colliderect(rect):
                    return True
                    
        return False
        
    def check_score(self, bird_x):
        """
        Перевірка проходження труби для зарахування рахунку.
        
        Args:
            bird_x: Позиція X птаха
            
        Returns:
            Поточний рахунок
        """
        for pipe in self.pipes:
            if not pipe.passed and pipe.x + pipe.width < bird_x:
                pipe.passed = True
                self.score += 1
                
        return self.score
        
    def draw(self, screen):
        """
        Малювання всіх труб.
        
        Args:
            screen: Екран pygame для малювання
        """
        for pipe in self.pipes:
            pipe.draw(screen)

