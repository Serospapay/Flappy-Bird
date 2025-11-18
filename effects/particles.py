"""
@file: particles.py
@description: Система частинок для візуальних ефектів (зіткнення, збір бонусів).
@dependencies: pygame, random, math
@created: 2024-12-19
"""

import pygame
import random
import math

class Particle:
    """Клас однієї частинки."""
    
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, lifetime=30, size=3):
        """
        Ініціалізація частинки.
        
        Args:
            x: float - Початкова координата X
            y: float - Початкова координата Y
            color: tuple - Колір частинки (R, G, B)
            velocity_x: float - Початкова швидкість X
            velocity_y: float - Початкова швидкість Y
            lifetime: int - Тривалість життя в кадрах
            size: int - Розмір частинки
        """
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255
        
    def update(self):
        """Оновлення частинки."""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.2  # Гравітація
        self.lifetime -= 1
        
        # Зменшення прозорості
        if self.max_lifetime > 0:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        return self.lifetime > 0
    
    def draw(self, screen):
        """
        Малювання частинки.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        if self.lifetime <= 0:
            return
        
        color_with_alpha = (*self.color, self.alpha)
        # Створення поверхні з альфа-каналом
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
        screen.blit(particle_surface, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    """Система керування частинками з Object Pooling для оптимізації."""
    
    def __init__(self, pool_size=200):
        """
        Ініціалізація системи частинок з Object Pooling.
        
        Args:
            pool_size: int - Розмір пулу частинок (зменшує GC)
        """
        self.particles = []
        self.pool_size = pool_size
        # Object Pool - пул неактивних частинок для перевикористання
        self.particle_pool = []
        self.active_count = 0
    
    def _get_particle(self, x, y, color, velocity_x=0, velocity_y=0, lifetime=30, size=3):
        """
        Отримати частинку з пулу або створити нову (Object Pooling).
        
        Args:
            x: float - Координата X
            y: float - Координата Y
            color: tuple - Колір
            velocity_x: float - Швидкість X
            velocity_y: float - Швидкість Y
            lifetime: int - Тривалість життя
            size: int - Розмір
            
        Returns:
            Particle - Активація частинки з пулу
        """
        # Спробувати отримати з пулу
        if self.particle_pool:
            particle = self.particle_pool.pop()
            # Переініціалізація
            particle.x = x
            particle.y = y
            particle.color = color
            particle.velocity_x = velocity_x
            particle.velocity_y = velocity_y
            particle.lifetime = lifetime
            particle.max_lifetime = lifetime
            particle.size = size
            particle.alpha = 255
            return particle
        else:
            # Створити нову якщо пул порожній
            return Particle(x, y, color, velocity_x, velocity_y, lifetime, size)
    
    def add_explosion(self, x, y, color=(255, 100, 100), count=20):
        """
        Додавання ефекту вибуху з використанням Object Pooling.
        
        Args:
            x: float - Координата X
            y: float - Координата Y
            color: tuple - Колір частинок
            count: int - Кількість частинок
        """
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            particle = self._get_particle(
                x, y, color,
                velocity_x=velocity_x,
                velocity_y=velocity_y,
                lifetime=random.randint(20, 40),
                size=random.randint(2, 5)
            )
            self.particles.append(particle)
            self.active_count += 1
    
    def add_coin_collect(self, x, y):
        """
        Додавання ефекту збору монети з використанням Object Pooling.
        
        Args:
            x: float - Координата X
            y: float - Координата Y
        """
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed - 2  # Вгору
            
            particle = self._get_particle(
                x, y, (255, 215, 0),  # Золотий
                velocity_x=velocity_x,
                velocity_y=velocity_y,
                lifetime=random.randint(15, 30),
                size=random.randint(2, 4)
            )
            self.particles.append(particle)
            self.active_count += 1
    
    def add_powerup_collect(self, x, y, color=(100, 200, 255)):
        """
        Додавання ефекту збору power-up з використанням Object Pooling.
        
        Args:
            x: float - Координата X
            y: float - Координата Y
            color: tuple - Колір ефекту
        """
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            particle = self._get_particle(
                x, y, color,
                velocity_x=velocity_x,
                velocity_y=velocity_y,
                lifetime=random.randint(20, 35),
                size=random.randint(2, 4)
            )
            self.particles.append(particle)
            self.active_count += 1
    
    def update(self):
        """Оновлення всіх частинок з поверненням в Object Pool."""
        new_particles = []
        for particle in self.particles:
            if particle.update():
                new_particles.append(particle)
            else:
                # Повернути в пул замість видалення
                if len(self.particle_pool) < self.pool_size:
                    self.particle_pool.append(particle)
                self.active_count -= 1
        
        self.particles = new_particles
    
    def draw(self, screen):
        """
        Малювання всіх частинок.
        
        Args:
            screen: pygame.Surface - Екран для малювання
        """
        for particle in self.particles:
            particle.draw(screen)

