"""
@file: bird.py
@description: Клас Bird (птах). Керує рухом, фізикою та малюванням птаха.
@dependencies: pygame, game_config
@created: 2024-12-19
"""

import pygame
import math
from src.game_config import GameConfig

class Bird:
    """Клас птаха (гравець)."""
    
    def __init__(self, x, y):
        """
        Ініціалізація птаха.
        
        Args:
            x: Початкова координата X
            y: Початкова координата Y
        """
        self.config = GameConfig()
        
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        
        self.velocity = 0
        self.rotation = 0
        
    def jump(self):
        """Стрибок птаха."""
        self.velocity = self.config.JUMP_STRENGTH
        
    def update(self):
        """Оновлення позиції та фізики птаха."""
        # Застосування гравітації
        self.velocity += self.config.GRAVITY
        
        # Оновлення позиції
        self.y += self.velocity
        
        # Обмеження максимальної швидкості падіння
        if self.velocity > 15:
            self.velocity = 15
            
        # Ротація в залежності від швидкості
        self.rotation = min(30, max(-90, self.velocity * 3))
        
    def get_rect(self):
        """Отримати прямокутник колізії."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        """
        Малювання птаха з сучасним стилем та деталізацією.
        
        Args:
            screen: Екран pygame для малювання
        """
        # Створення поверхні для ротації (більша для тіні та ефектів)
        bird_surface = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)
        offset_x, offset_y = 15, 15
        
        # М'яка тінь птаха (більша та розмита)
        for i in range(3):
            shadow_alpha = 30 - i * 10
            shadow_ellipse = pygame.Rect(offset_x + 2 + i, offset_y + 2 + i, 
                                       self.width + 2, self.height + 2)
            pygame.draw.ellipse(bird_surface, (0, 0, 0, shadow_alpha), shadow_ellipse)
        
        # Основне тіло птаха - сучасніший дизайн
        body_rect = pygame.Rect(offset_x, offset_y, self.width, self.height)
        
        # Градієнт для тіла (від світлого до темного)
        body_colors = [
            (255, 240, 180),  # Світло-жовтий верх
            (255, 220, 100),  # Жовтий
            (255, 200, 50),   # Золотий
            (255, 180, 30),   # Темніший золотий
        ]
        
        for y in range(self.height):
            ratio = y / self.height
            # Плавний перехід кольорів
            if ratio < 0.25:
                color = body_colors[0]
            elif ratio < 0.5:
                t = (ratio - 0.25) / 0.25
                color = tuple(int(body_colors[0][i] * (1-t) + body_colors[1][i] * t) for i in range(3))
            elif ratio < 0.75:
                t = (ratio - 0.5) / 0.25
                color = tuple(int(body_colors[1][i] * (1-t) + body_colors[2][i] * t) for i in range(3))
            else:
                t = (ratio - 0.75) / 0.25
                color = tuple(int(body_colors[2][i] * (1-t) + body_colors[3][i] * t) for i in range(3))
            
            pygame.draw.line(bird_surface, color, 
                           (body_rect.left, body_rect.top + y),
                           (body_rect.right, body_rect.top + y))
        
        # Світлий відблиск на верхній частині (більш реалістичний)
        highlight_rect = pygame.Rect(offset_x + 6, offset_y + 4, self.width - 12, self.height // 2)
        pygame.draw.ellipse(bird_surface, (255, 255, 200, 120), highlight_rect)
        # Додатковий маленький відблиск
        small_highlight = pygame.Rect(offset_x + 10, offset_y + 6, self.width // 2, self.height // 3)
        pygame.draw.ellipse(bird_surface, (255, 255, 255, 100), small_highlight)
        
        # Текстура пір'я (горизонтальні лінії)
        for i in range(1, 4):
            feather_y = offset_y + self.height * i // 4
            feather_start = offset_x + 8
            feather_end = offset_x + self.width - 5
            # Світліші лінії для текстури
            pygame.draw.line(bird_surface, (255, 230, 150, 80), 
                           (feather_start, feather_y), (feather_end, feather_y), 1)
        
        # Обведення тіла (більш м'яке)
        pygame.draw.ellipse(bird_surface, (220, 200, 120, 180), body_rect, 2)
        
        # Крила (анімація + деталізація)
        wing_animation = int(3 * abs(math.sin(pygame.time.get_ticks() * 0.015)))
        
        # Верхнє крило
        upper_wing = [
            (offset_x + self.width // 2 - 3, offset_y + self.height // 2 - 3),
            (offset_x + self.width // 2 - 18, offset_y + self.height // 2 - 10 - wing_animation),
            (offset_x + self.width // 2 - 12, offset_y + self.height // 2 - 6),
            (offset_x + self.width // 2 - 5, offset_y + self.height // 2 - 2),
        ]
        pygame.draw.polygon(bird_surface, (255, 190, 80), upper_wing)
        pygame.draw.polygon(bird_surface, (230, 170, 60), upper_wing, 2)
        
        # Нижнє крило (менше)
        lower_wing = [
            (offset_x + self.width // 2 - 3, offset_y + self.height // 2 + 3),
            (offset_x + self.width // 2 - 12, offset_y + self.height // 2 + 6),
            (offset_x + self.width // 2 - 8, offset_y + self.height // 2 + 4),
        ]
        pygame.draw.polygon(bird_surface, (240, 180, 70), lower_wing)
        pygame.draw.polygon(bird_surface, (220, 160, 50), lower_wing, 1)
        
        # Дзьоб з покращеною деталізацією
        beak_base_x = offset_x + self.width
        beak_tip_x = offset_x + self.width + 14
        beak_center_y = offset_y + self.height // 2
        
        # Основний дзьоб з градієнтом
        beak_points = [
            (beak_base_x, beak_center_y),
            (beak_tip_x, beak_center_y - 7),
            (beak_tip_x, beak_center_y + 7)
        ]
        
        # Градієнт для дзьоба
        for i in range(len(beak_points) - 1):
            p1 = beak_points[i]
            p2 = beak_points[i + 1]
            # Від світло-помаранчевого до темного
            for j in range(8):
                t = j / 8
                x = int(p1[0] * (1-t) + p2[0] * t)
                y = int(p1[1] * (1-t) + p2[1] * t)
                color_ratio = j / 8
                r = int(255 * (1 - color_ratio * 0.3))
                g = int(200 * (1 - color_ratio * 0.3))
                b = int(100 * (1 - color_ratio * 0.3))
                pygame.draw.circle(bird_surface, (r, g, b), (x, y), 3)
        
        # Основний контур дзьоба
        pygame.draw.polygon(bird_surface, (255, 180, 50), beak_points)
        # Яскравіша верхня частина
        beak_highlight = [
            (beak_base_x + 2, beak_center_y - 2),
            (beak_tip_x - 2, beak_center_y - 5),
            (beak_tip_x - 2, beak_center_y - 1),
        ]
        pygame.draw.polygon(bird_surface, (255, 230, 100), beak_highlight)
        # Межа дзьоба
        pygame.draw.polygon(bird_surface, (200, 140, 40), beak_points, 2)
        
        # Око з реалістичними деталями
        eye_center_x = offset_x + self.width - 8
        eye_center_y = offset_y + self.height // 2 - 4
        
        # Зовнішнє обведення ока
        pygame.draw.circle(bird_surface, (80, 50, 30), (eye_center_x, eye_center_y), 9, 2)
        
        # Білок ока
        pygame.draw.circle(bird_surface, (255, 255, 255), (eye_center_x, eye_center_y), 7)
        
        # Внутрішнє обведення
        pygame.draw.circle(bird_surface, (50, 30, 20), (eye_center_x, eye_center_y), 7, 1)
        
        # Зіниця (більша та реалістичніша)
        pupil_offset_x = max(-2, min(2, int(self.rotation / 20)))
        pygame.draw.circle(bird_surface, (0, 0, 0), 
                          (eye_center_x + pupil_offset_x, eye_center_y), 5)
        
        # Відблиск на оці (більший)
        pygame.draw.circle(bird_surface, (255, 255, 255), 
                          (eye_center_x + 2 + pupil_offset_x, eye_center_y - 2), 3)
        # Додатковий маленький відблиск
        pygame.draw.circle(bird_surface, (255, 255, 255), 
                          (eye_center_x + 3 + pupil_offset_x, eye_center_y - 1), 1)
        
        # Деталі пір'я на спині (більш реалістичні)
        for i in range(4):
            feather_x = offset_x + 6 + i * 7
            feather_y = offset_y + 4 + i * 2
            # Основна лінія пір'я
            pygame.draw.line(bird_surface, (240, 210, 130), 
                           (feather_x, feather_y), 
                           (feather_x - 4, feather_y - 3), 2)
            # Деталі
            pygame.draw.line(bird_surface, (255, 230, 150), 
                           (feather_x - 1, feather_y - 1), 
                           (feather_x - 3, feather_y - 2), 1)
        
        # Хвіст (якщо птах летить вниз)
        if self.rotation < -30:
            tail_points = [
                (offset_x - 2, offset_y + self.height // 2),
                (offset_x - 8, offset_y + self.height // 2 - 4),
                (offset_x - 8, offset_y + self.height // 2 + 4),
            ]
            pygame.draw.polygon(bird_surface, (240, 200, 90), tail_points)
            pygame.draw.polygon(bird_surface, (220, 180, 70), tail_points, 1)
        
        # Ротація з антиаліасингом
        rotated_surface = pygame.transform.rotate(bird_surface, -self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        
        screen.blit(rotated_surface, rotated_rect)

