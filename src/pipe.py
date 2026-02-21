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
    TYPE_MOVING = "moving"
    TYPE_SHRINKING = "shrinking"
    TYPE_SPIKES = "spikes"  # Шипи на краях проміжку
    TYPE_SPLIT = "split"  # Роздвоєний проміжок (верх/низ)
    
    def __init__(self, x, gap_y, gap_size, config, pipe_type=TYPE_NORMAL, rng=None):
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
        
        r = rng or random
        self.split_offset = r.uniform(-0.3, 0.3) * gap_size if pipe_type == Pipe.TYPE_SPLIT else 0
        
        # Верхня труба (гарантуємо int)
        self.top_height = int(gap_y)
        # Нижня труба (гарантуємо int)
        self.bottom_y = int(gap_y + gap_size)
        self.bottom_height = int(config.SCREEN_HEIGHT - self.bottom_y)
        
    def update(self, speed=None):
        """Оновлення позиції труби. speed - фактична швидкість (з урахуванням slow_time)."""
        actual_speed = speed if speed is not None else self.config.PIPE_SPEED
        self.x -= actual_speed
        
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
        """Отримати прямокутники колізій (верхня та нижня труба + голови + шипи/бар'єр)."""
        rects = []
        
        # Шипи (TYPE_SPIKES) - маленькі трикутники на краях проміжку
        if self.type == Pipe.TYPE_SPIKES:
            spike_h = 15
            rects.append(pygame.Rect(self.x, int(self.gap_y) - spike_h, self.width, spike_h))
            rects.append(pygame.Rect(self.x, int(self.bottom_y), self.width, spike_h))
        
        # Бар'єр для TYPE_SPLIT - перегородка посередині проміжку
        if self.type == Pipe.TYPE_SPLIT:
            barrier_y = int(self.gap_y + self.gap_size * 0.4 + self.split_offset)
            rects.append(pygame.Rect(self.x, barrier_y, self.width, 25))
        
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
        
    def _draw_cylinder_body(self, screen, x, y, w, h, color, head_color, dark_color):
        """Малювання тіла труби з pseudo-3D: блік зліва, тінь справа."""
        strip_w = max(1, w // 5)
        light = tuple(min(255, c + 45) for c in color)
        pygame.draw.rect(screen, light, (x, y, strip_w, h))
        pygame.draw.rect(screen, color, (x + strip_w, y, w - strip_w * 2, h))
        pygame.draw.rect(screen, dark_color, (x + w - strip_w, y, strip_w, h))
    
    def _draw_cap(self, screen, x, y, w, h, color, head_color, dark_color):
        """Шапка труби: +5px з кожного боку, 30px висота, pseudo-3D."""
        cap_w = w + 10
        cap_x = x - 5
        strip_w = max(1, cap_w // 5)
        light = tuple(min(255, c + 45) for c in head_color)
        pygame.draw.rect(screen, light, (cap_x, y, strip_w, h))
        pygame.draw.rect(screen, head_color, (cap_x + strip_w, y, cap_w - strip_w * 2, h))
        pygame.draw.rect(screen, dark_color, (cap_x + cap_w - strip_w, y, strip_w, h))
    
    def draw(self, screen):
        """
        Малювання труби: pseudo-3D циліндр, шапка на кінці (біля проміжку).
        """
        if self.type == Pipe.TYPE_MOVING:
            color = (100, 150, 255)
            head_color = (50, 100, 200)
            dark_color = (30, 70, 150)
        elif self.type == Pipe.TYPE_SHRINKING:
            color = (255, 150, 100)
            head_color = (200, 100, 50)
            dark_color = (180, 80, 30)
        elif self.type == Pipe.TYPE_SPIKES:
            color = (180, 60, 60)
            head_color = (140, 40, 40)
            dark_color = (100, 20, 20)
        elif self.type == Pipe.TYPE_SPLIT:
            color = (100, 180, 100)
            head_color = (60, 140, 60)
            dark_color = (40, 100, 40)
        else:
            color = self.config.PIPE_COLOR
            head_color = self.config.PIPE_HEAD_COLOR
            dark_color = (20, 80, 20)
        
        cap_h = 30
        top_height_int = int(self.top_height)
        bottom_y_int = int(self.bottom_y)
        bottom_height_int = int(self.bottom_height)
        
        # Верхня труба: тіло + шапка внизу (біля проміжку)
        body_top_h = max(0, top_height_int - cap_h)
        self._draw_cylinder_body(screen, self.x, 0, self.width, body_top_h, color, head_color, dark_color)
        self._draw_cap(screen, self.x, body_top_h, self.width, cap_h, color, head_color, dark_color)
        
        # Нижня труба: шапка вгорі (біля проміжку) + тіло
        self._draw_cap(screen, self.x, bottom_y_int, self.width, cap_h, color, head_color, dark_color)
        body_bot_h = max(0, bottom_height_int - cap_h)
        self._draw_cylinder_body(screen, self.x, bottom_y_int + cap_h, self.width, body_bot_h, color, head_color, dark_color)
        
        # Шипи (TYPE_SPIKES)
        if self.type == Pipe.TYPE_SPIKES:
            spike_h, spike_w = 15, 8
            for sx in range(0, self.width, spike_w + 4):
                pts_top = [(self.x + sx, top_height_int), (self.x + sx + spike_w//2, top_height_int - spike_h), (self.x + sx + spike_w, top_height_int)]
                pts_bot = [(self.x + sx, bottom_y_int), (self.x + sx + spike_w//2, bottom_y_int + spike_h), (self.x + sx + spike_w, bottom_y_int)]
                pygame.draw.polygon(screen, dark_color, pts_top)
                pygame.draw.polygon(screen, dark_color, pts_bot)
        
        # Бар'єр (TYPE_SPLIT)
        if self.type == Pipe.TYPE_SPLIT:
            barrier_y = int(self.gap_y + self.gap_size * 0.4 + self.split_offset)
            self._draw_cylinder_body(screen, self.x, barrier_y, self.width, 25, head_color, color, dark_color)


class PipeManager:
    """Менеджер для керування всіма трубами."""
    
    def __init__(self, config, random_gen=None):
        """
        Ініціалізація менеджера труб.
        
        Args:
            config: Об'єкт GameConfig
        """
        self.config = config
        self.pipes = []
        self.last_spawn_time = 0
        self.score = 0
        self._rng = random_gen or random  # Для Daily Challenge - детермінований RNG
        
    def spawn_pipe(self, current_time, score=0):
        """Створення нової труби, якщо пройшов достатній час."""
        if current_time - self.last_spawn_time >= self.config.PIPE_SPAWN_INTERVAL:
            gap_y = self._rng.randint(
                self.config.PIPE_HEAD_HEIGHT + 50,
                self.config.SCREEN_HEIGHT - self.config.PIPE_GAP - self.config.PIPE_HEAD_HEIGHT - 50
            )
            
            # Визначення типу труби в залежності від складності
            types_pool = [Pipe.TYPE_NORMAL]
            if score > 10:
                types_pool.extend([Pipe.TYPE_MOVING])
            if score > 15:
                types_pool.extend([Pipe.TYPE_SPIKES])
            if score > 20:
                types_pool.extend([Pipe.TYPE_SHRINKING])
            if score > 30:
                types_pool.extend([Pipe.TYPE_SPLIT])
            pipe_type = self._rng.choice(types_pool)
            
            new_pipe = Pipe(
                self.config.SCREEN_WIDTH,
                gap_y,
                self.config.PIPE_GAP,
                self.config,
                pipe_type,
                self._rng
            )
            self.pipes.append(new_pipe)
            self.last_spawn_time = current_time
            
    def update(self, score=0, speed=None):
        """Оновлення всіх труб. speed - фактична швидкість (з урахуванням slow_time)."""
        current_time = pygame.time.get_ticks()
        self.spawn_pipe(current_time, score)
        
        actual_speed = speed if speed is not None else self.config.PIPE_SPEED
        
        # Оновлення труб
        for pipe in self.pipes[:]:
            pipe.update(actual_speed)
            
            # Видалення труб, що вийшли за межі екрану
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)
                
    def check_collision(self, bird, ghost_active=False):
        """
        Перевірка колізій птаха з трубами.
        
        Args:
            bird: Об'єкт Bird
            ghost_active: bool - Ghost power-up активний (прохід крізь труби)
            
        Returns:
            True якщо є колізія, False інакше
        """
        if bird is None or ghost_active:
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

