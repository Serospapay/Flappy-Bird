"""
@file: game.py
@description: Головний файл гри Flappy Bird. Керує ігровим циклом, станами гри та загальною логікою.
@dependencies: pygame, bird, pipe, game_config, save_system, sound_manager, achievements, 
               particles, powerups, background, difficulty_manager
@created: 2024-12-19
"""

import pygame
import sys
import time
import random
from bird import Bird
from pipe import PipeManager
from game_config import GameConfig
from save_system import SaveSystem
from sound_manager import SoundManager
from achievements import AchievementSystem
from particles import ParticleSystem
from powerups import PowerUpManager
from background import ParallaxBackground
from difficulty_manager import DifficultyManager
from ui_elements import Button, Text, Panel
from camera_effects import CameraEffects
from score_animation import ScoreAnimationSystem

class FlappyBirdGame:
    """Головний клас гри Flappy Bird."""
    
    def __init__(self):
        """Ініціалізація гри."""
        pygame.init()
        
        self.config = GameConfig()
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Enhanced Edition")
        self.clock = pygame.time.Clock()
        
        # Завантаження даних збереження
        self.save_data = SaveSystem.load()
        self.best_score = self.save_data.get("best_score", 0)
        
        # Системи
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.save_data.get("settings", {}).get("music_volume", 0.5))
        self.sound_manager.set_sfx_volume(self.save_data.get("settings", {}).get("sfx_volume", 0.7))
        
        self.particle_system = ParticleSystem()
        self.background = ParallaxBackground(self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        self.difficulty_manager = DifficultyManager(self.config)
        self.camera_effects = CameraEffects()
        self.score_animations = ScoreAnimationSystem()
        
        # Стани гри: 'menu', 'playing', 'paused', 'game_over', 'settings', 'achievements', 'statistics'
        self.state = 'menu'
        self.paused = False
        self.menu_selection = 0
        self.menu_options = ['Грати', 'Налаштування', 'Досягнення', 'Статистика', 'Вихід']
        self.settings_selection = 0  # Вибір налаштування
        
        # Ігрові об'єкти
        self.bird = None
        self.pipe_manager = None
        self.powerup_manager = None
        self.score = 0
        self.coins = 0
        self.game_start_time = 0
        self.last_collision = False
        
        # Статистика гри
        self.powerups_used = 0
        self.perfect_run = 0
        
        # Шрифти
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # UI елементи
        self.menu_buttons = []
        self._should_exit = False
        self.setup_menu_buttons()
    
    def setup_menu_buttons(self):
        """Налаштування кнопок меню."""
        center_x = self.config.SCREEN_WIDTH // 2
        start_y = self.config.SCREEN_HEIGHT // 2
        
        self.menu_buttons = [
            Button(center_x, start_y, 250, 50, 'Грати', self.font_medium,
                   lambda: self.start_game(),
                   bg_color=(100, 150, 200), hover_color=(150, 200, 255)),
            Button(center_x, start_y + 60, 250, 50, 'Налаштування', self.font_medium,
                   lambda: setattr(self, 'state', 'settings'),
                   bg_color=(100, 150, 200), hover_color=(150, 200, 255)),
            Button(center_x, start_y + 120, 250, 50, 'Досягнення', self.font_medium,
                   lambda: setattr(self, 'state', 'achievements'),
                   bg_color=(100, 150, 200), hover_color=(150, 200, 255)),
            Button(center_x, start_y + 180, 250, 50, 'Статистика', self.font_medium,
                   lambda: setattr(self, 'state', 'statistics'),
                   bg_color=(100, 150, 200), hover_color=(150, 200, 255)),
            Button(center_x, start_y + 240, 250, 50, 'Вихід', self.font_medium,
                   lambda: setattr(self, '_should_exit', True),
                   bg_color=(150, 80, 80), hover_color=(200, 100, 100)),
        ]
        
    def start_game(self):
        """Почати нову гру."""
        self.bird = Bird(self.config.SCREEN_WIDTH // 4, self.config.SCREEN_HEIGHT // 2)
        self.pipe_manager = PipeManager(self.config)
        self.powerup_manager = PowerUpManager(self.config)
        self.score = 0
        self.coins = 0
        self.state = 'playing'
        self.paused = False
        self.game_start_time = time.time()
        self.last_collision = False
        self.powerups_used = 0
        self.perfect_run = 0
        self.particle_system.particles.clear()
        self.score_animations.animations.clear()
        self.camera_effects.fade_in(30)
        
        # Відновлення базових параметрів складності
        self.config.PIPE_GAP = 200
        self.config.PIPE_SPEED = 4
        self.config.PIPE_SPAWN_INTERVAL = 1800
        
        self.sound_manager.play_sound('jump')
    
    def _adjust_setting(self, direction):
        """Зміна налаштування."""
        settings = self.save_data.setdefault("settings", {})
        
        if self.settings_selection == 0:  # Гучність музики
            current = settings.get("music_volume", 0.5)
            new_volume = max(0.0, min(1.0, current + direction * 0.1))
            settings["music_volume"] = round(new_volume, 1)
            self.sound_manager.set_music_volume(new_volume)
            self.sound_manager.play_sound('jump')
        elif self.settings_selection == 1:  # Гучність звуків
            current = settings.get("sfx_volume", 0.7)
            new_volume = max(0.0, min(1.0, current + direction * 0.1))
            settings["sfx_volume"] = round(new_volume, 1)
            self.sound_manager.set_sfx_volume(new_volume)
            self.sound_manager.play_sound('jump')
        elif self.settings_selection == 2:  # Складність
            difficulties = ["easy", "normal", "hard"]
            current = settings.get("difficulty", "normal")
            try:
                current_idx = difficulties.index(current)
                new_idx = (current_idx + direction) % len(difficulties)
                settings["difficulty"] = difficulties[new_idx]
                self.sound_manager.play_sound('jump')
            except ValueError:
                settings["difficulty"] = "normal"
        
    def handle_events(self):
        """Обробка подій."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'playing':
                        # Пауза або game over
                        if not self.paused:
                            self.paused = True
                            self.camera_effects.fade_out(10)
                        else:
                            self.paused = False
                            self.camera_effects.fade_in(10)
                    elif self.state == 'paused':
                        self.paused = False
                        self.camera_effects.fade_in(10)
                    elif self.state == 'game_over':
                        self.state = 'menu'
                        self.camera_effects.fade_in(20)
                        self.menu_selection = 0
                    elif self.state == 'settings':
                        # Збереження налаштувань перед виходом
                        SaveSystem.save(self.save_data)
                        self.state = 'menu'
                        self.camera_effects.fade_in(20)
                        self.menu_selection = 0
                        self.settings_selection = 0
                    elif self.state in ['achievements', 'statistics']:
                        self.state = 'menu'
                        self.camera_effects.fade_in(20)
                        self.menu_selection = 0
                    else:
                        return False
                
                elif self.state == 'menu':
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                        self.sound_manager.play_sound('jump')
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                        self.sound_manager.play_sound('jump')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if 0 <= self.menu_selection < len(self.menu_buttons):
                            self.menu_buttons[self.menu_selection].callback()
                
                elif self.state == 'playing':
                    if event.key == pygame.K_SPACE:
                        if self.paused:
                            # Продовжити гру з паузи
                            self.paused = False
                            self.camera_effects.fade_in(10)
                        elif self.bird:
                            self.bird.jump()
                            self.sound_manager.play_sound('jump')
                
                elif self.state == 'settings':
                    # Навігація по налаштуваннях
                    if event.key == pygame.K_UP:
                        self.settings_selection = (self.settings_selection - 1) % 4
                        self.sound_manager.play_sound('jump')
                    elif event.key == pygame.K_DOWN:
                        self.settings_selection = (self.settings_selection + 1) % 4
                        self.sound_manager.play_sound('jump')
                    elif event.key == pygame.K_LEFT:
                        self._adjust_setting(-1)
                    elif event.key == pygame.K_RIGHT:
                        self._adjust_setting(1)
                
                elif self.state == 'game_over':
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_game()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = (event.button == 1)
            else:
                mouse_clicked = False
                
            # Оновлення кнопок для hover ефекту
            if self.state == 'menu' and event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for button in self.menu_buttons:
                    button.update(mouse_pos, False)
                        
        # Оновлення стану кнопок
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_clicked = mouse_buttons[0] if mouse_buttons else False
        
        if self.state == 'menu':
            for button in self.menu_buttons:
                button.update(mouse_pos, mouse_clicked)
        
        if self._should_exit:
            return False
                        
        return True
    
    def handle_menu_selection(self):
        """Обробка вибору в меню."""
        option = self.menu_options[self.menu_selection]
        
        if option == 'Грати':
            self.start_game()
        elif option == 'Налаштування':
            self.state = 'settings'
        elif option == 'Досягнення':
            self.state = 'achievements'
        elif option == 'Статистика':
            self.state = 'statistics'
        elif option == 'Вихід':
            SaveSystem.save(self.save_data)
            return False
        
        self.sound_manager.play_sound('jump')
        
    def update(self):
        """Оновлення ігрової логіки."""
        # Оновлення ефектів камери та анімацій
        self.camera_effects.update()
        self.score_animations.update()
        
        if self.state == 'playing' and not self.paused:
            if self.bird is None or self.pipe_manager is None or self.powerup_manager is None:
                return
            
            # Застосування складності
            self.difficulty_manager.apply_difficulty(self.pipe_manager, self.score)
            
            # Застосування повільного часу
            speed_multiplier = self.powerup_manager.get_speed_multiplier()
            actual_speed = self.config.PIPE_SPEED * speed_multiplier
            
            # Оновлення фону
            self.background.update(actual_speed)
            
            # Оновлення птаха
            self.bird.update()
            
            # Оновлення труб
            self.pipe_manager.update(self.score)
            
            # Оновлення power-ups
            self.powerup_manager.update(pygame.time.get_ticks())
            
            # Перевірка колізій з power-ups
            collected_powerups = self.powerup_manager.check_collision(self.bird)
            for powerup_type in collected_powerups:
                if powerup_type == 'coin':
                    self.coins += 1
                    self.sound_manager.play_sound('coin')
                    self.particle_system.add_coin_collect(self.bird.x + self.bird.width // 2, self.bird.y + self.bird.height // 2)
                else:
                    self.powerups_used += 1
                    self.sound_manager.play_sound('powerup')
                    self.particle_system.add_powerup_collect(self.bird.x + self.bird.width // 2, self.bird.y + self.bird.height // 2)
            
            # Перевірка колізій з трубами
            collision = self.pipe_manager.check_collision(self.bird)
            if collision:
                # Перевірка щита
                if self.powerup_manager.has_shield():
                    if self.powerup_manager.use_shield():
                        self.sound_manager.play_sound('powerup')
                        self.last_collision = False
                else:
                    if not self.last_collision:
                        self.sound_manager.play_sound('collision')
                        self.particle_system.add_explosion(self.bird.x + self.bird.width // 2, self.bird.y + self.bird.height // 2)
                        # Ефект shake камери при колізії
                        self.camera_effects.add_shake(intensity=15, duration=20)
                    self.last_collision = True
                    self.game_over()
                    return
            else:
                self.last_collision = False
                self.perfect_run += 1
            
            # Перевірка виходу за межі екрану
            if self.bird.y + self.bird.height > self.config.SCREEN_HEIGHT or self.bird.y < 0:
                if not self.last_collision:
                    self.sound_manager.play_sound('collision')
                    self.particle_system.add_explosion(self.bird.x + self.bird.width // 2, self.bird.y + self.bird.height // 2)
                    # Ефект shake камери при колізії
                    self.camera_effects.add_shake(intensity=15, duration=20)
                self.last_collision = True
                self.game_over()
                return
            
            # Перевірка проходження труби (рахунок)
            new_score = self.pipe_manager.check_score(self.bird.x)
            if new_score > self.score:
                # Подвійні очки
                score_increase = 1
                if self.powerup_manager.is_double_score_active():
                    score_increase = 2
                
                old_score = self.score
                self.score = new_score
                if score_increase > 1:
                    self.score += score_increase - 1
                    self.pipe_manager.score = self.score
                
                # Анімація зміни рахунку
                actual_increase = self.score - old_score
                self.score_animations.add_score_change(
                    self.config.SCREEN_WIDTH // 2,
                    100,
                    actual_increase,
                    (255, 255, 100) if score_increase > 1 else (255, 255, 150)
                )
                
                self.sound_manager.play_sound('coin')
            
            # Спорадична генерація power-ups
            if len(collected_powerups) == 0 and len(self.powerup_manager.powerups) == 0:
                if pygame.time.get_ticks() % 5000 < 16:  # Приблизно кожні 5 секунд
                    if self.score > 5 and len(self.pipe_manager.pipes) > 0:
                        last_pipe = self.pipe_manager.pipes[-1]
                        if last_pipe.x < self.config.SCREEN_WIDTH - 200:
                            if self.powerup_manager.spawn_chance > random.random():
                                gap_center = last_pipe.gap_y + last_pipe.gap_size // 2
                                self.powerup_manager.spawn_powerup(
                                    self.config.SCREEN_WIDTH,
                                    gap_center
                                )
            
            # Оновлення частинок
            self.particle_system.update()
            
            # Перевірка досягнень
            game_state = {
                'score': self.score,
                'coins_collected': self.save_data.get("statistics", {}).get("coins_collected", 0) + self.coins,
                'powerups_used': self.save_data.get("statistics", {}).get("powerups_used", 0) + self.powerups_used,
                'perfect_run': self.perfect_run,
                'total_games': self.save_data.get("total_games", 0)
            }
            new_achievements = AchievementSystem.check_achievements(
                game_state,
                self.save_data.get("achievements", [])
            )
            
            for ach_id in new_achievements:
                SaveSystem.unlock_achievement(self.save_data, ach_id)
                self.sound_manager.play_sound('achievement')
                
    def game_over(self):
        """Обробка завершення гри."""
        time_played = int(time.time() - self.game_start_time)
        
        # Оновлення статистики
        SaveSystem.update_statistics(
            self.save_data,
            self.score,
            time_played,
            self.coins
        )
        
        # Перевірка нового рекорду
        if self.score > self.best_score:
            self.best_score = self.score
        
        # Збереження даних
        SaveSystem.save(self.save_data)
        
        self.state = 'game_over'
        
    def draw_menu(self):
        """Малювання меню з покращеним візуальним оформленням."""
        self.background.draw(self.screen)
        
        # Overlay з градієнтом
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.config.SCREEN_HEIGHT):
            alpha = int(100 + (y / self.config.SCREEN_HEIGHT) * 80)
            overlay.fill((0, 0, 0, min(180, alpha)), 
                        (0, y, self.config.SCREEN_WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        # Панель для заголовка
        title_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, 30,
            400, 150,
            bg_color=(40, 60, 100), alpha=180,
            border_color=(150, 200, 255), border_width=3,
            shadow=True
        )
        title_panel.draw(self.screen)
        
        # Заголовок з тінню та обведенням
        title_text = Text("Flappy Bird", self.font_large, 
                         color=(255, 255, 100),
                         shadow=True, shadow_color=(0, 0, 0), shadow_offset=(3, 3),
                         outline=True, outline_color=(50, 50, 150), outline_width=2)
        title_text.draw(self.screen, (self.config.SCREEN_WIDTH // 2, 80), center=True)
        
        subtitle_text = Text("Enhanced Edition", self.font_small,
                           color=(200, 220, 255),
                           shadow=True, shadow_color=(0, 0, 0))
        subtitle_text.draw(self.screen, (self.config.SCREEN_WIDTH // 2, 140), center=True)
        
        # Малювання кнопок
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        # Панель для найкращого рахунку
        if self.best_score > 0:
            score_panel = Panel(
                self.config.SCREEN_WIDTH // 2 - 180, self.config.SCREEN_HEIGHT - 80,
                360, 50,
                bg_color=(50, 100, 50), alpha=200,
                border_color=(150, 255, 150), border_width=2,
                shadow=True
            )
            score_panel.draw(self.screen)
            
            best_text = Text(f"Найкращий рахунок: {self.best_score}", self.font_small,
                           color=(255, 255, 150),
                           shadow=True, shadow_color=(0, 0, 0))
            best_text.draw(self.screen, (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 55), center=True)
            
    def draw_game(self):
        """Малювання ігрового екрану з покращеним UI."""
        # Створення проміжної поверхні для shake ефекту
        game_surface = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        
        # Фон
        self.background.draw(game_surface)
        
        # Труби
        if self.pipe_manager:
            self.pipe_manager.draw(game_surface)
        
        # Power-ups
        if self.powerup_manager:
            self.powerup_manager.draw(game_surface)
            
        # Птах
        if self.bird:
            self.bird.draw(game_surface)
        
        # Частинки
        self.particle_system.draw(game_surface)
        
        # Анімації рахунку
        self.score_animations.draw(game_surface, self.font_medium)
        
        # Застосування shake ефекту
        if not self.camera_effects.apply_shake(self.screen, game_surface):
            self.screen.blit(game_surface, (0, 0))
            
        # Панель рахунку з градієнтом
        score_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 90, 5,
            180, 65,
            bg_color=(30, 50, 80), alpha=200,
            border_color=(150, 200, 255), border_width=2,
            shadow=True
        )
        score_panel.draw(self.screen)
        
        # Рахунок з тінню та обведенням
        score_text = Text(str(self.score), self.font_medium,
                         color=(255, 255, 150),
                         shadow=True, shadow_color=(0, 0, 0), shadow_offset=(2, 2),
                         outline=True, outline_color=(50, 100, 150), outline_width=1)
        score_text.draw(self.screen, (self.config.SCREEN_WIDTH // 2, 37), center=True)
        
        # Панель монет
        coin_panel = Panel(
            self.config.SCREEN_WIDTH - 130, 5,
            120, 45,
            bg_color=(80, 60, 30), alpha=200,
            border_color=(255, 215, 150), border_width=2,
            shadow=True
        )
        coin_panel.draw(self.screen)
        
        # Монети з тінню
        coin_text = Text(f"🪙 {self.coins}", self.font_small,
                        color=(255, 215, 0),
                        shadow=True, shadow_color=(0, 0, 0))
        coin_text.draw(self.screen, (self.config.SCREEN_WIDTH - 70, 27), center=True)
        
        # Fade overlay (для переходів)
        self.camera_effects.draw_fade(self.screen)
        
        # Меню паузи
        if self.paused:
            self.draw_pause_menu()
        
    def draw_game_over(self):
        """Малювання екрану Game Over з покращеним візуальним оформленням."""
        self.draw_game()
        
        # Overlay з градієнтом
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.config.SCREEN_HEIGHT):
            alpha = int(150 + (abs(y - self.config.SCREEN_HEIGHT // 2) / (self.config.SCREEN_HEIGHT // 2)) * 105)
            overlay.fill((0, 0, 0, min(255, alpha)), 
                        (0, y, self.config.SCREEN_WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        # Панель Game Over
        game_over_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 250, self.config.SCREEN_HEIGHT // 2 - 150,
            500, 300,
            bg_color=(60, 20, 20), alpha=220,
            border_color=(255, 100, 100), border_width=3,
            shadow=True
        )
        game_over_panel.draw(self.screen)
        
        # Game Over текст з тінню та обведенням
        game_over_text = Text("Game Over", self.font_large,
                             color=(255, 50, 50),
                             shadow=True, shadow_color=(0, 0, 0), shadow_offset=(4, 4),
                             outline=True, outline_color=(150, 0, 0), outline_width=2)
        game_over_text.draw(self.screen, 
                           (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 - 100), 
                           center=True)
        
        # Фінальний рахунок
        final_score_text = Text(f"Рахунок: {self.score}", self.font_medium,
                               color=(255, 255, 255),
                               shadow=True, shadow_color=(0, 0, 0))
        final_score_text.draw(self.screen, 
                             (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 - 30), 
                             center=True)
        
        # Найкращий рахунок
        best_text = Text(f"Найкращий: {self.best_score}", self.font_small,
                        color=(255, 215, 0),
                        shadow=True, shadow_color=(0, 0, 0))
        best_text.draw(self.screen, 
                      (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 20), 
                      center=True)
        
        # Монети
        coin_text = Text(f"Монети: {self.coins}", self.font_small,
                        color=(255, 215, 0),
                        shadow=True, shadow_color=(0, 0, 0))
        coin_text.draw(self.screen, 
                      (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 60), 
                      center=True)
        
        # Інструкція
        restart_text = Text("Натисніть SPACE для рестарту", self.font_small,
                           color=(200, 200, 200),
                           shadow=True, shadow_color=(0, 0, 0))
        restart_text.draw(self.screen, 
                         (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 110), 
                         center=True)
        
    def draw_achievements(self):
        """Малювання екрану досягнень з покращеним візуальним оформленням."""
        # Фон з градієнтом
        for y in range(self.config.SCREEN_HEIGHT):
            ratio = y / self.config.SCREEN_HEIGHT
            r = int(30 * (1 + ratio * 0.5))
            g = int(30 * (1 + ratio * 0.5))
            b = int(50 * (1 + ratio * 0.5))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.config.SCREEN_WIDTH, y))
        
        # Панель заголовка
        title_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, 30,
            400, 80,
            bg_color=(40, 60, 100), alpha=220,
            border_color=(150, 200, 255), border_width=3,
            shadow=True
        )
        title_panel.draw(self.screen)
        
        title_text = Text("Досягнення", self.font_large,
                         color=(255, 255, 150),
                         shadow=True, shadow_color=(0, 0, 0), shadow_offset=(3, 3),
                         outline=True, outline_color=(50, 100, 150), outline_width=2)
        title_text.draw(self.screen, (self.config.SCREEN_WIDTH // 2, 70), center=True)
        
        # Панель досягнень
        achievement_panel = Panel(
            50, 130,
            self.config.SCREEN_WIDTH - 100, self.config.SCREEN_HEIGHT - 200,
            bg_color=(20, 30, 50), alpha=200,
            border_color=(100, 150, 200), border_width=2,
            shadow=True
        )
        achievement_panel.draw(self.screen)
        
        unlocked = self.save_data.get("achievements", [])
        y_offset = 150
        count = 0
        
        for ach_id, achievement in AchievementSystem.ACHIEVEMENTS.items():
            if count >= 8:  # Показуємо максимум 8 на екран
                break
                
            is_unlocked = ach_id in unlocked
            text_color = (200, 255, 200) if is_unlocked else (100, 100, 100)
            prefix = "✓ " if is_unlocked else "✗ "
            
            ach_text = Text(f"{prefix}{achievement.name}: {achievement.description}", 
                          self.font_small,
                          color=text_color,
                          shadow=True, shadow_color=(0, 0, 0))
            ach_text.draw(self.screen, (70, y_offset))
            y_offset += 45
            count += 1
        
        back_text = Text("Натисніть ESC для повернення", self.font_small,
                        color=(150, 150, 150),
                        shadow=True, shadow_color=(0, 0, 0))
        back_text.draw(self.screen, 
                      (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 50), 
                      center=True)
        
    def draw_statistics(self):
        """Малювання екрану статистики з покращеним візуальним оформленням."""
        # Фон з градієнтом
        for y in range(self.config.SCREEN_HEIGHT):
            ratio = y / self.config.SCREEN_HEIGHT
            r = int(30 * (1 + ratio * 0.5))
            g = int(30 * (1 + ratio * 0.5))
            b = int(50 * (1 + ratio * 0.5))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.config.SCREEN_WIDTH, y))
        
        # Панель заголовка
        title_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, 30,
            400, 80,
            bg_color=(40, 60, 100), alpha=220,
            border_color=(150, 200, 255), border_width=3,
            shadow=True
        )
        title_panel.draw(self.screen)
        
        title_text = Text("Статистика", self.font_large,
                         color=(255, 255, 150),
                         shadow=True, shadow_color=(0, 0, 0), shadow_offset=(3, 3),
                         outline=True, outline_color=(50, 100, 150), outline_width=2)
        title_text.draw(self.screen, (self.config.SCREEN_WIDTH // 2, 70), center=True)
        
        # Панель статистики
        stats_panel = Panel(
            100, 130,
            self.config.SCREEN_WIDTH - 200, self.config.SCREEN_HEIGHT - 200,
            bg_color=(20, 30, 50), alpha=200,
            border_color=(100, 150, 200), border_width=2,
            shadow=True
        )
        stats_panel.draw(self.screen)
        
        stats = self.save_data.get("statistics", {})
        y_offset = 150
        
        stat_items = [
            ("Найкращий рахунок", stats.get("best_score", 0)),
            ("Середній рахунок", stats.get("average_score", 0.0)),
            ("Всього ігор", self.save_data.get("total_games", 0)),
            ("Всього очок", self.save_data.get("total_score", 0)),
            ("Зібрано монет", stats.get("coins_collected", 0)),
            ("Досягнень", len(self.save_data.get("achievements", []))),
        ]
        
        for label, value in stat_items:
            stat_text = Text(f"{label}: {value}", self.font_small,
                           color=(200, 220, 255),
                           shadow=True, shadow_color=(0, 0, 0))
            stat_text.draw(self.screen, (120, y_offset))
            y_offset += 50
        
        back_text = Text("Натисніть ESC для повернення", self.font_small,
                        color=(150, 150, 150),
                        shadow=True, shadow_color=(0, 0, 0))
        back_text.draw(self.screen, 
                      (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 50), 
                      center=True)
        
    def draw_settings(self):
        """Малювання екрану налаштувань з покращеним візуальним оформленням."""
        # Фон з градієнтом
        for y in range(self.config.SCREEN_HEIGHT):
            ratio = y / self.config.SCREEN_HEIGHT
            r = int(30 * (1 + ratio * 0.5))
            g = int(30 * (1 + ratio * 0.5))
            b = int(50 * (1 + ratio * 0.5))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.config.SCREEN_WIDTH, y))
        
        # Панель заголовка
        title_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, 30,
            400, 80,
            bg_color=(40, 60, 100), alpha=220,
            border_color=(150, 200, 255), border_width=3,
            shadow=True
        )
        title_panel.draw(self.screen)
        
        title_text = Text("Налаштування", self.font_large,
                         color=(255, 255, 150),
                         shadow=True, shadow_color=(0, 0, 0), shadow_offset=(3, 3),
                         outline=True, outline_color=(50, 100, 150), outline_width=2)
        title_text.draw(self.screen, (self.config.SCREEN_WIDTH // 2, 70), center=True)
        
        # Панель налаштувань
        settings_panel = Panel(
            100, 130,
            self.config.SCREEN_WIDTH - 200, self.config.SCREEN_HEIGHT - 200,
            bg_color=(20, 30, 50), alpha=200,
            border_color=(100, 150, 200), border_width=2,
            shadow=True
        )
        settings_panel.draw(self.screen)
        
        settings = self.save_data.get("settings", {})
        y_offset = 150
        
        settings_info = [
            ("Гучність музики", f"{int(settings.get('music_volume', 0.5) * 100)}%"),
            ("Гучність звуків", f"{int(settings.get('sfx_volume', 0.7) * 100)}%"),
            ("Складність", settings.get('difficulty', 'normal')),
            ("Тема", settings.get('theme', 'default')),
        ]
        
        for i, (label, value) in enumerate(settings_info):
            # Виділення вибраного налаштування
            color = (255, 255, 100) if i == self.settings_selection else (200, 220, 255)
            prefix = "> " if i == self.settings_selection else "  "
            
            setting_text = Text(f"{prefix}{label}: {value}", self.font_small,
                               color=color,
                               shadow=True, shadow_color=(0, 0, 0))
            setting_text.draw(self.screen, (120, y_offset))
            
            # Підказка для вибраного налаштування
            if i == self.settings_selection:
                hint_text = Text("← → для зміни", self.font_tiny,
                               color=(150, 200, 255),
                               shadow=True, shadow_color=(0, 0, 0))
                hint_text.draw(self.screen, (self.config.SCREEN_WIDTH - 200, y_offset))
            
            y_offset += 60
        
        info_text = Text("↑↓ для вибору, ←→ для зміни, ESC для збереження та виходу", self.font_tiny,
                        color=(150, 150, 150),
                        shadow=True, shadow_color=(0, 0, 0))
        info_text.draw(self.screen, 
                      (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 100), 
                      center=True)
        
        back_text = Text("Натисніть ESC для повернення", self.font_small,
                        color=(150, 150, 150),
                        shadow=True, shadow_color=(0, 0, 0))
        back_text.draw(self.screen, 
                      (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 50), 
                      center=True)
        
    def draw_pause_menu(self):
        """Малювання меню паузи."""
        # Overlay
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Панель паузи
        pause_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, self.config.SCREEN_HEIGHT // 2 - 100,
            400, 200,
            bg_color=(40, 60, 100), alpha=220,
            border_color=(150, 200, 255), border_width=3,
            shadow=True
        )
        pause_panel.draw(self.screen)
        
        # Текст паузи
        pause_text = Text("ПАУЗА", self.font_large,
                         color=(255, 255, 100),
                         shadow=True, shadow_color=(0, 0, 0), shadow_offset=(3, 3),
                         outline=True, outline_color=(50, 100, 150), outline_width=2)
        pause_text.draw(self.screen, 
                       (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 - 50), 
                       center=True)
        
        # Інструкції
        instruction_text = Text("Натисніть SPACE або ESC для продовження", self.font_small,
                               color=(200, 200, 200),
                               shadow=True, shadow_color=(0, 0, 0))
        instruction_text.draw(self.screen, 
                             (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 30), 
                             center=True)
    
    def draw(self):
        """Малювання поточного стану."""
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'game_over':
            self.draw_game_over()
        elif self.state == 'achievements':
            self.draw_achievements()
        elif self.state == 'statistics':
            self.draw_statistics()
        elif self.state == 'settings':
            self.draw_settings()
        
        # Fade overlay для всіх станів (якщо активний)
        self.camera_effects.draw_fade(self.screen)
            
        pygame.display.flip()
        
    def run(self):
        """Головний ігровий цикл."""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run()
