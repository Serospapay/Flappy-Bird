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

from src.bird import Bird
from src.pipe import PipeManager
from src.game_config import GameConfig
from systems.save_system import SaveSystem
from systems.sound_manager import SoundManager
from systems.achievements import AchievementSystem
from effects.particles import ParticleSystem
from systems.powerups import PowerUpManager
from systems.background import ParallaxBackground
from systems.difficulty_manager import DifficultyManager
from systems.skins import SkinSystem
from systems.game_modes import GameModes
from ui.ui_elements import Button, Text, Panel
from ui.theme import (
    PANEL_HEADER, PANEL_DARK, PANEL_ALPHA, PANEL_ALPHA_LIGHT,
    BORDER_COLOR, BORDER_WIDTH,
    TEXT_ACCENT, TEXT_ACCENT_GOLD, TEXT_MUTED, COIN_COLOR,
    ACCENT_PRIMARY, ACCENT_HOVER, SECONDARY_BG, SECONDARY_HOVER, DANGER_BG, DANGER_HOVER,
    SUCCESS_BG, SUCCESS_HOVER, HUD_PANEL_BG, HUD_COIN_BG, SHADOW_COLOR
)
from ui.hud_elements import PowerUpIndicator, ComboCounter, DifficultyIndicator
from ui.slider import Slider
from ui.toast import ToastSystem
from effects.camera_effects import CameraEffects
from effects.score_animation import ScoreAnimationSystem
from effects.flash_effects import FlashSystem

class FlappyBirdGame:
    """Головний клас гри Flappy Bird."""
    
    def __init__(self):
        """Ініціалізація гри."""
        pygame.init()
        
        self.config = GameConfig()
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Drift Quest - Demo Edition")
        self.clock = pygame.time.Clock()
        
        # Завантаження даних збереження
        self.save_data = SaveSystem.load()
        self.best_score = self.save_data.get("best_score", 0)
        
        # Демо-режим: відкрити все
        DEMO_MODE = True
        self.demo_mode = DEMO_MODE
        if self.demo_mode:
            self.save_data["unlocked_skins"] = list(SkinSystem.SKINS.keys())
            self.save_data["achievements"] = list(AchievementSystem.ACHIEVEMENTS.keys())
            self.save_data["statistics"] = self.save_data.get("statistics", {})
            self.save_data["statistics"]["coins_collected"] = max(
                self.save_data["statistics"].get("coins_collected", 0), 999
            )
        
        # Системи
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.save_data.get("settings", {}).get("music_volume", 0.5))
        self.sound_manager.set_sfx_volume(self.save_data.get("settings", {}).get("sfx_volume", 0.7))
        
        self.particle_system = ParticleSystem()
        theme = self.save_data.get("settings", {}).get("theme", "light")
        self.background = ParallaxBackground(self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT, theme)
        self.difficulty_manager = DifficultyManager(self.config)
        self.camera_effects = CameraEffects()
        self.score_animations = ScoreAnimationSystem()
        self.flash_system = FlashSystem()

        # Стани гри
        self.state = 'menu'
        self.paused = False
        self.menu_selection = 0
        self.game_mode = GameModes.MODE_NORMAL
        self.challenge_id = None
        self.menu_options = ['Грати', 'Щоденний виклик', 'Скіни', 'Налаштування', 'Досягнення', 'Статистика', 'Вихід']
        self.settings_selection = 0  # Вибір налаштування
        
        # Ігрові об'єкти
        self.bird = None
        self.pipe_manager = None
        self.powerup_manager = None
        self.score = 0
        self.coins = 0
        self.game_start_time = 0
        self.last_collision = False
        self.last_pipe_score = -1  # Для combo system
        
        # Статистика гри
        self.powerups_used = 0
        self.perfect_run = 0
        
        # Шрифти (спочатку шрифти!)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 24)
        self.font_hint = pygame.font.Font(None, 20)
        
        # HUD елементи (після шрифтів!)
        self.toast_system = ToastSystem(self.config.SCREEN_WIDTH)
        self.combo_counter = ComboCounter(self.config.SCREEN_WIDTH // 2, 100, self.font_small)
        self.combo_counter.show_minimum = True  # Показувати тільки важливі комбінації
        self.difficulty_indicator = DifficultyIndicator(10, 80, 200, 50, self.font_tiny)
        self.difficulty_indicator.show = False  # Приховати за замовчуванням (не відволікає)
        self.powerup_indicators = {}  # Індикатори активних power-ups (type -> PowerUpIndicator)
        self.powerup_spawn_interval_ms = 5000
        self.challenge_params = {}
        self._last_tension_flash_ms = 0
        self._last_powerup_spawn_attempt_ms = 0
        self._jump_count = 0
        
        # UI елементи
        self.menu_buttons = []
        self.settings_sliders = []
        self.settings_buttons = []
        self.skin_buttons = []
        self._should_exit = False
        self.setup_menu_buttons()
        self.setup_settings_sliders()
    
    def setup_menu_buttons(self):
        """Налаштування кнопок меню: фіксовані розміри, чітка сітка 2x2."""
        cx = self.config.SCREEN_WIDTH // 2
        gap_x, gap_y = 20, 20
        
        # Головні: 350x60, по центру екрана
        main_w, main_h = 350, 60
        main_y1, main_y2 = 210, 285
        btn_play = Button(cx, main_y1, main_w, main_h, 'Грати', self.font_medium,
                         lambda: self._start_with_mode(GameModes.MODE_NORMAL),
                         bg_color=ACCENT_PRIMARY, hover_color=ACCENT_HOVER,
                         border_radius=12, hover_scale=1.03)
        btn_daily = Button(cx, main_y2, main_w, main_h, 'Щоденний виклик', self.font_medium,
                          lambda: self._start_with_mode(GameModes.MODE_DAILY),
                          bg_color=ACCENT_PRIMARY, hover_color=ACCENT_HOVER,
                          border_radius=12, hover_scale=1.03)
        
        # Сітка 2x2: ширина 220, centerx строго
        sec_w, sec_h = 220, 50
        sec_left_cx = cx - 120
        sec_right_cx = cx + 120
        sec_row1_y = 370
        sec_row2_y = sec_row1_y + sec_h + gap_y
        btn_skins = Button(sec_left_cx, sec_row1_y, sec_w, sec_h, 'Скіни', self.font_small,
                          lambda: self._enter_skins(),
                          bg_color=SECONDARY_BG, hover_color=SECONDARY_HOVER,
                          border_radius=10, hover_scale=1.02)
        btn_settings = Button(sec_right_cx, sec_row1_y, sec_w, sec_h, 'Налаштування', self.font_small,
                             lambda: self._enter_settings(),
                             bg_color=SECONDARY_BG, hover_color=SECONDARY_HOVER,
                             border_radius=10, hover_scale=1.02)
        btn_achievements = Button(sec_left_cx, sec_row2_y, sec_w, sec_h, 'Досягнення', self.font_small,
                                 lambda: setattr(self, 'state', 'achievements'),
                                 bg_color=SECONDARY_BG, hover_color=SECONDARY_HOVER,
                                 border_radius=10, hover_scale=1.02)
        btn_statistics = Button(sec_right_cx, sec_row2_y, sec_w, sec_h, 'Статистика', self.font_small,
                               lambda: setattr(self, 'state', 'statistics'),
                               bg_color=SECONDARY_BG, hover_color=SECONDARY_HOVER,
                               border_radius=10, hover_scale=1.02)
        
        # Вихід: 140x50, праворуч знизу
        exit_w, exit_h = 140, 50
        exit_x = self.config.SCREEN_WIDTH - 85
        exit_y = self.config.SCREEN_HEIGHT - 60
        btn_exit = Button(exit_x, exit_y, exit_w, exit_h, 'Вихід', self.font_small,
                         lambda: setattr(self, '_should_exit', True),
                         bg_color=DANGER_BG, hover_color=DANGER_HOVER,
                         border_radius=10, hover_scale=1.02)
        
        self.menu_buttons = [
            btn_play, btn_daily, btn_skins, btn_settings,
            btn_achievements, btn_statistics, btn_exit
        ]
    
    def _enter_settings(self):
        """Перехід в екран налаштувань."""
        self.state = 'settings'
        self.setup_settings_sliders()
        self.setup_settings_buttons()
    
    def _enter_skins(self):
        """Перехід в екран скінів."""
        self.state = 'skins'
        self.setup_skins_buttons()
    
    def setup_settings_sliders(self):
        """Слайдери гучності: centerx = screen_width // 2, рівномірні Y (+70)."""
        settings = self.save_data.get("settings", {})
        cx = self.config.SCREEN_WIDTH // 2
        slider_width = 350
        slider_height = 40
        
        def on_music_change(value):
            s = self.save_data.setdefault("settings", {})
            s["music_volume"] = round(value, 2)
            self.sound_manager.set_music_volume(value)
        
        def on_sfx_change(value):
            s = self.save_data.setdefault("settings", {})
            s["sfx_volume"] = round(value, 2)
            self.sound_manager.set_sfx_volume(value)
            self.sound_manager.play_sound('jump')
        
        slider_x = cx - slider_width // 2
        self.settings_sliders = [
            Slider(slider_x, 100, slider_width, slider_height,
                   0.0, 1.0, settings.get("music_volume", 0.5),
                   self.font_small, "Гучність музики", on_music_change),
            Slider(slider_x, 170, slider_width, slider_height,
                   0.0, 1.0, settings.get("sfx_volume", 0.7),
                   self.font_small, "Гучність звуків", on_sfx_change),
        ]
    
    def setup_settings_buttons(self):
        """Кнопки Складність і Тема: 350x50, centerx = screen_width // 2."""
        settings = self.save_data.get("settings", {})
        cx = self.config.SCREEN_WIDTH // 2
        btn_w, btn_h = 350, 50
        diff_val = settings.get("difficulty", "normal")
        theme_val = "темна" if settings.get("theme", "light") == "dark" else "світла"
        
        def cycle_difficulty():
            self.settings_selection = 0
            self._adjust_setting(1)
            self.setup_settings_buttons()
        
        def cycle_theme():
            self.settings_selection = 1
            self._adjust_setting(1)
            self.setup_settings_buttons()
        
        self.settings_buttons = [
            Button(cx, 260, btn_w, btn_h, f"Складність: {diff_val}", self.font_small,
                   cycle_difficulty, bg_color=SECONDARY_BG, hover_color=SECONDARY_HOVER,
                   border_radius=10),
            Button(cx, 330, btn_w, btn_h, f"Тема: {theme_val}", self.font_small,
                   cycle_theme, bg_color=SECONDARY_BG, hover_color=SECONDARY_HOVER,
                   border_radius=10),
        ]
        
    def _start_with_mode(self, mode):
        """Почати гру з обраним режимом."""
        self.game_mode = mode
        self.challenge_id = None
        self.start_game()
    
    def start_game(self):
        """Почати нову гру."""
        skin_id = self.save_data.get("equipped_skin", "default")
        self.bird = Bird(self.config.SCREEN_WIDTH // 4, self.config.SCREEN_HEIGHT // 2, skin_id)
        rng = GameModes.get_daily_random() if self.game_mode == GameModes.MODE_DAILY else None
        self.pipe_manager = PipeManager(self.config, rng, demo_mode=self.demo_mode)
        self.powerup_manager = PowerUpManager(self.config)
        self.powerup_spawn_interval_ms = 5000
        if self.demo_mode:
            # Demo: частіше бонуси для швидшого проходження і демонстрації механік.
            self.powerup_manager.spawn_chance = 0.7
            self.powerup_spawn_interval_ms = 2000
        self.score = 0
        self.coins = 0
        self.state = 'playing'
        self.paused = False
        self.game_start_time = time.time()
        self.last_collision = False
        self.powerups_used = 0
        self.perfect_run = 0
        self.last_pipe_score = -1
        self.particle_system.particles.clear()
        self.score_animations.animations.clear()
        self.toast_system.toasts.clear()
        self.combo_counter.reset_combo()
        self.powerup_indicators.clear()
        self.camera_effects.fade_in(30)
        self.challenge_params = {}
        self._jump_count = 0
        
        # Відновлення базових параметрів складності
        self.config.PIPE_GAP = GameConfig.PIPE_GAP
        self.config.PIPE_SPEED = GameConfig.PIPE_SPEED
        self.config.PIPE_SPAWN_INTERVAL = GameConfig.PIPE_SPAWN_INTERVAL

        # Режим challenge: параметри застосовуються централізовано при старті раунду
        if self.game_mode == GameModes.MODE_CHALLENGE and self.challenge_id:
            self.challenge_params = GameModes.get_challenge_params(self.challenge_id)
            speed_mult = float(self.challenge_params.get("speed_mult", 1.0))
            gap_mult = float(self.challenge_params.get("gap_mult", 1.0))
            self.config.PIPE_SPEED = max(1.0, self.config.PIPE_SPEED * speed_mult)
            self.config.PIPE_GAP = max(self.config.MIN_PIPE_GAP, int(self.config.PIPE_GAP * gap_mult))

        now_ms = pygame.time.get_ticks()
        self._last_tension_flash_ms = now_ms
        self._last_powerup_spawn_attempt_ms = now_ms
        
        self.sound_manager.play_sound('jump')
    
    def _adjust_setting(self, direction):
        """Зміна налаштування."""
        settings = self.save_data.setdefault("settings", {})
        if self.settings_selection == 0:  # Складність
            difficulties = ["easy", "normal", "hard"]
            current = settings.get("difficulty", "normal")
            try:
                current_idx = difficulties.index(current)
                new_idx = (current_idx + direction) % len(difficulties)
                settings["difficulty"] = difficulties[new_idx]
                self.sound_manager.play_sound('jump')
            except ValueError:
                settings["difficulty"] = "normal"
        elif self.settings_selection == 1:  # Тема
            themes = ["light", "dark"]
            current = settings.get("theme", "light")
            if current not in themes:
                current = "light"
            idx = (themes.index(current) + direction) % len(themes)
            settings["theme"] = themes[idx]
            self.background.set_theme(themes[idx])
            self.sound_manager.play_sound('jump')
        
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
                    elif self.state in ['achievements', 'statistics', 'skins']:
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
                    if event.key == pygame.K_DOWN:
                        if self.bird and self.bird.dash():
                            self.sound_manager.play_sound('powerup')
                    elif event.key == pygame.K_SPACE:
                        if self.paused:
                            # Продовжити гру з паузи
                            self.paused = False
                            self.camera_effects.fade_in(10)
                        elif self.bird:
                            self.bird.jump()
                            self._jump_count += 1
                            self.sound_manager.play_sound('jump')
                
                elif self.state == 'settings':
                    pass  # Налаштування: керування через слайдери та кнопки
                
                elif self.state == 'game_over':
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_game()
                        
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
        
        if self.state == 'settings':
            for slider in self.settings_sliders:
                slider.update(mouse_pos, mouse_clicked)
            for btn in self.settings_buttons:
                btn.update(mouse_pos, mouse_clicked)
        if self.state == 'skins':
            for btn in self.skin_buttons:
                btn.update(mouse_pos, mouse_clicked)
        
        if self._should_exit:
            return False
                        
        return True

    def update(self):
        """Оновлення ігрової логіки."""
        # Оновлення ефектів камери та анімацій
        self.camera_effects.update()
        self.score_animations.update()
        self.flash_system.update()
        self.toast_system.update()
        self.combo_counter.update()
        
        if self.state == 'playing' and not self.paused:
            if self.bird is None or self.pipe_manager is None or self.powerup_manager is None:
                return
            now_ms = pygame.time.get_ticks()
            
            # Застосування складності
            self.difficulty_manager.apply_difficulty(self.pipe_manager, self.score)
            
            # Оновлення індикатора складності
            difficulty_level = min(1.0, self.score / 50.0)  # Максимальна складність на 50 очках
            self.difficulty_indicator.update(difficulty_level)
            
            # Оновлення індикаторів power-ups (компактно внизу)
            active_effects = self.powerup_manager.active_effects
            x_start = self.config.SCREEN_WIDTH - 80  # Справа
            y_start = self.config.SCREEN_HEIGHT - 70  # Знизу
            
            active_count = sum(1 for e in active_effects.values() if e['active'])
            spacing = 55 if active_count > 0 else 0
            active_types = []
            
            for i, (effect_name, effect_data) in enumerate(active_effects.items()):
                if effect_data['active']:
                    active_types.append(effect_name)
                    target_y = y_start - i * spacing
                    indicator = self.powerup_indicators.get(effect_name)
                    if indicator is None:
                        indicator = PowerUpIndicator(
                            effect_name,
                            effect_data['duration'],
                            effect_data.get('max_duration', 600),
                            x_start,
                            target_y,
                            self.font_tiny
                        )
                        self.powerup_indicators[effect_name] = indicator
                    else:
                        indicator.x = x_start
                        indicator.y = target_y
                        indicator.max_duration = effect_data.get('max_duration', 600)
                        indicator.update(effect_data['duration'])

            # Видаляємо неактивні індикатори, щоб не накопичувати зайві об'єкти
            stale_types = [t for t in self.powerup_indicators.keys() if t not in active_types]
            for stale_type in stale_types:
                del self.powerup_indicators[stale_type]
            
            # Застосування повільного часу (впливає на фон, труби та power-ups)
            speed_multiplier = self.powerup_manager.get_speed_multiplier()
            actual_speed = self.config.PIPE_SPEED * speed_multiplier
            
            # Оновлення фону
            self.background.update(actual_speed)
            
            # Оновлення птаха
            self.bird.update()
            
            # Оновлення труб (з урахуванням slow_time)
            self.pipe_manager.update(self.score, actual_speed)
            
            # Оновлення power-ups (з урахуванням slow_time)
            self.powerup_manager.update(now_ms, actual_speed)
            
            # Синхронізація Ghost з power-up до птаха
            if self.powerup_manager.is_ghost_active():
                eff = self.powerup_manager.active_effects['ghost']
                self.bird.ghost_active = True
                self.bird.ghost_duration = eff['duration']
            
            # Перевірка колізій з power-ups
            no_powerups_mode = bool(self.challenge_params.get("no_powerups", False))
            if no_powerups_mode and self.powerup_manager.powerups:
                self.powerup_manager.powerups.clear()
            collected_powerups = [] if no_powerups_mode else self.powerup_manager.check_collision(self.bird)
            for powerup_type in collected_powerups:
                if powerup_type == 'coin':
                    self.coins += 1
                    self.sound_manager.play_sound('coin')
                    self.particle_system.add_coin_collect(self.bird.x + self.bird.width // 2, self.bird.y + self.bird.height // 2)
                else:
                    self.powerups_used += 1
                    self.sound_manager.play_sound('powerup')
                    self.particle_system.add_powerup_collect(self.bird.x + self.bird.width // 2, self.bird.y + self.bird.height // 2)
            
            # Перевірка колізій з трубами (ghost = прохід крізь труби)
            ghost_active = self.powerup_manager.is_ghost_active()
            collision = self.pipe_manager.check_collision(self.bird, ghost_active)
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
                
                # Перевірка наближення до труби (небезпека)
                if self.pipe_manager and self.pipe_manager.pipes:
                    forward_pipes = [p for p in self.pipe_manager.pipes if p.x + p.width > self.bird.x]
                    if forward_pipes:
                        closest_pipe = min(forward_pipes, key=lambda p: p.x - self.bird.x)
                        distance = closest_pipe.x - self.bird.x
                        if 0 < distance < 100:
                            self.sound_manager.set_music_mood("tension")
                            if now_ms - self._last_tension_flash_ms >= 500:
                                self.flash_system.add_danger_flash()
                                self._last_tension_flash_ms = now_ms
            
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
                # Combo system - перевірка чи це нова труба
                if self.score == self.last_pipe_score + 1:
                    # Послідовне проходження - додаємо combo
                    self.combo_counter.add_combo()
                else:
                    # Перервано серію (без toast для меншого відволікання)
                    # if self.combo_counter.combo >= 5:
                    #     self.toast_system.add_toast(f"Серію перервано! Макс: x{self.combo_counter.max_combo}", 'warning', 120)
                    self.combo_counter.reset_combo()
                    self.combo_counter.add_combo()  # Починаємо нову серію
                
                self.last_pipe_score = self.score
                self.sound_manager.set_music_mood("calm")
                
                # Подвійні очки
                score_increase = 1
                if self.powerup_manager.is_double_score_active():
                    score_increase = 2
                
                # Combo bonus (без toast для меншого відволікання, тільки візуальний індикатор)
                combo_bonus = self.combo_counter.get_combo_bonus()
                if combo_bonus > 0:
                    score_increase += combo_bonus
                    # self.toast_system.add_toast(f"Combo бонус +{combo_bonus}!", 'combo', 120)  # Вимкнено
                
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
                
                # Короткий flash при наборі очок (тільки для подвійних очок)
                if actual_increase >= 2:
                    self.flash_system.add_score_flash()
            
            # Спорадична генерація power-ups
            if (not no_powerups_mode and len(collected_powerups) == 0 and len(self.powerup_manager.powerups) == 0
                and now_ms - self._last_powerup_spawn_attempt_ms >= self.powerup_spawn_interval_ms):
                self._last_powerup_spawn_attempt_ms = now_ms
                required_score = 0 if self.demo_mode else 5
                if self.score >= required_score and len(self.pipe_manager.pipes) > 0:
                    last_pipe = self.pipe_manager.pipes[-1]
                    if last_pipe.x < self.config.SCREEN_WIDTH - 200:
                        if self.powerup_manager.spawn_chance > random.random():
                            gap_center = last_pipe.gap_y + last_pipe.gap_size // 2
                            self.powerup_manager.spawn_powerup(
                                self.config.SCREEN_WIDTH,
                                gap_center
                            )

            # Обмеження challenge-режимів (якщо ввімкнені)
            max_jumps = self.challenge_params.get("max_jumps")
            if max_jumps is not None and self._jump_count > int(max_jumps):
                self.game_over()
                return
            
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
                # Flash ефект при досягненні
                self.flash_system.add_achievement_flash()
                # Toast notification (коротше)
                ach_name = AchievementSystem.ACHIEVEMENTS.get(ach_id, None)
                if ach_name:
                    self.toast_system.add_toast(f"{ach_name.name}!", 'achievement', 120)  # Коротший час
                
    def game_over(self):
        """Обробка завершення гри."""
        time_played = int(time.time() - self.game_start_time)
        
        # Оновлення статистики (включає total_games, powerups_used)
        SaveSystem.update_statistics(
            self.save_data,
            self.score,
            time_played,
            self.coins,
            self.powerups_used
        )
        
        # Перевірка досягнень після оновлення статистики (для "Вижив" та інших)
        game_state = {
            'score': self.score,
            'coins_collected': self.save_data.get("statistics", {}).get("coins_collected", 0),
            'powerups_used': self.save_data.get("statistics", {}).get("powerups_used", 0),
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
            self.flash_system.add_achievement_flash()
            ach_name = AchievementSystem.ACHIEVEMENTS.get(ach_id, None)
            if ach_name:
                self.toast_system.add_toast(f"{ach_name.name}!", 'achievement', 120)
        
        # Перевірка нового рекорду
        if self.score > self.best_score:
            self.best_score = self.score
            # Flash ефект при новому рекорді
            self.flash_system.add_record_flash()
            # Toast notification (коротше)
            self.toast_system.add_toast(f"Рекорд: {self.score}!", 'record', 120)  # Коротший час
        
        # Збереження даних
        SaveSystem.save(self.save_data)
        
        self.state = 'game_over'
        
    def draw_menu(self):
        """Малювання меню: чистий layout без перевантажених рамок."""
        self.background.draw(self.screen)
        
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.config.SCREEN_HEIGHT):
            alpha = int(100 + (y / self.config.SCREEN_HEIGHT) * 80)
            overlay.fill((0, 0, 0, min(180, alpha)), (0, y, self.config.SCREEN_WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        cx = self.config.SCREEN_WIDTH // 2
        title_str = "Neon Drift Quest"
        title_surf = self.font_large.render(title_str, True, TEXT_ACCENT)
        title_rect = title_surf.get_rect(center=(cx, 75))
        shadow_surf = self.font_large.render(title_str, True, SHADOW_COLOR)
        self.screen.blit(shadow_surf, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title_surf, title_rect)
        
        Text("Arcade Demo Edition", self.font_small, color=TEXT_MUTED, shadow=True,
             outline=False).draw(self.screen, (cx, 125), center=True)
        
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        if self.best_score > 0:
            Text(f"Найкращий рахунок: {self.best_score}", self.font_small,
                 color=TEXT_ACCENT_GOLD, shadow=True, outline=False).draw(
                self.screen, (cx, self.config.SCREEN_HEIGHT - 50), center=True)
            
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
            # Щит або ghost: напівпрозоре коло (малюємо під птахом)
            shield_active = self.powerup_manager and self.powerup_manager.has_shield()
            if shield_active or (self.bird.ghost_active and self.bird.ghost_duration > 0):
                cx = int(self.bird.x + self.bird.width // 2)
                cy = int(self.bird.y + self.bird.height // 2)
                r = max(self.bird.width, self.bird.height) // 2 + 18
                shield_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(shield_surf, (100, 200, 255, 120), (r + 2, r + 2), r)
                game_surface.blit(shield_surf, (cx - r - 2, cy - r - 2))
            self.bird.draw(game_surface)
        
        # Частинки
        self.particle_system.draw(game_surface)
        
        # Анімації рахунку
        self.score_animations.draw(game_surface, self.font_medium)
        
        # Застосування shake ефекту
        if not self.camera_effects.apply_shake(self.screen, game_surface):
            self.screen.blit(game_surface, (0, 0))
            
        score_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 60, 5, 120, 40,
            bg_color=HUD_PANEL_BG, alpha=PANEL_ALPHA_LIGHT,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=False
        )
        score_panel.draw(self.screen)
        Text(str(self.score), self.font_medium, color=TEXT_ACCENT,
             shadow=True, outline=False).draw(self.screen, (self.config.SCREEN_WIDTH // 2, 25), center=True)
        
        coin_icon_x = self.config.SCREEN_WIDTH - 52
        coin_icon_y = 22
        pygame.draw.circle(self.screen, (255, 215, 0), (coin_icon_x, coin_icon_y), 12)
        pygame.draw.circle(self.screen, (255, 140, 0), (coin_icon_x, coin_icon_y), 12, 2)
        Text(str(self.coins), self.font_tiny, color=COIN_COLOR, shadow=True).draw(
            self.screen, (coin_icon_x + 20, coin_icon_y), center=True)
        
        # HUD елементи (мінімалістичні)
        # Combo counter (показується тільки коли >= 5)
        self.combo_counter.draw(self.screen)
        
        # Difficulty indicator (прихований за замовчуванням)
        # self.difficulty_indicator.draw(self.screen)  # Приховано для мінімального відволікання
        
        # Power-up indicators (компактні, справа знизу)
        for indicator in self.powerup_indicators.values():
            indicator.draw(self.screen)
        
        # Toast notifications (менш нав'язливі, коротші)
        self.toast_system.draw(self.screen, self.font_tiny)  # Менший шрифт
        
        # Flash ефекти
        self.flash_system.draw(self.screen)
        
        # Fade overlay (для переходів)
        self.camera_effects.draw_fade(self.screen)
        
        # Меню паузи
        if self.paused:
            self.draw_pause_menu()
        
    def draw_game_over(self):
        """Малювання екрану Game Over з покращеним візуальним оформленням."""
        self.draw_game()
        
        # Flash ефекти на екрані game over
        self.flash_system.draw(self.screen)
        
        # Overlay з градієнтом
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.config.SCREEN_HEIGHT):
            alpha = int(150 + (abs(y - self.config.SCREEN_HEIGHT // 2) / (self.config.SCREEN_HEIGHT // 2)) * 105)
            overlay.fill((0, 0, 0, min(255, alpha)), 
                        (0, y, self.config.SCREEN_WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        game_over_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 250, self.config.SCREEN_HEIGHT // 2 - 150,
            500, 300,
            bg_color=DANGER_BG, alpha=PANEL_ALPHA,
            border_color=(180, 80, 80), border_width=BORDER_WIDTH, shadow=True
        )
        game_over_panel.draw(self.screen)
        
        Text("Game Over", self.font_large, color=(220, 80, 80),
             shadow=True, outline=False).draw(self.screen,
            (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 - 100), center=True)
        Text(f"Рахунок: {self.score}", self.font_medium, color=TEXT_ACCENT,
             shadow=True).draw(self.screen,
            (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 - 30), center=True)
        Text(f"Найкращий: {self.best_score}", self.font_small, color=COIN_COLOR,
             shadow=True).draw(self.screen,
            (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 20), center=True)
        Text(f"Монети: {self.coins}", self.font_small, color=COIN_COLOR,
             shadow=True).draw(self.screen,
            (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 60), center=True)
        Text("Натисніть SPACE для рестарту", self.font_small, color=TEXT_MUTED,
             shadow=True).draw(self.screen,
            (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 110), center=True)
        
    def draw_achievements(self):
        """Малювання екрану досягнень."""
        for y in range(self.config.SCREEN_HEIGHT):
            ratio = y / self.config.SCREEN_HEIGHT
            r = int(25 * (1 + ratio * 0.5))
            g = int(30 * (1 + ratio * 0.5))
            b = int(45 * (1 + ratio * 0.5))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.config.SCREEN_WIDTH, y))
        
        title_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, 30, 400, 80,
            bg_color=PANEL_HEADER, alpha=PANEL_ALPHA,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=True
        )
        title_panel.draw(self.screen)
        Text("Досягнення", self.font_large, color=TEXT_ACCENT,
             shadow=True, outline=False).draw(self.screen, (self.config.SCREEN_WIDTH // 2, 70), center=True)
        
        achievement_panel = Panel(
            50, 130, self.config.SCREEN_WIDTH - 100, self.config.SCREEN_HEIGHT - 200,
            bg_color=PANEL_DARK, alpha=PANEL_ALPHA,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=True
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
            
            Text(f"{prefix}{achievement.name}: {achievement.description}",
                 self.font_small, color=text_color, shadow=True).draw(self.screen, (70, y_offset))
            y_offset += 45
            count += 1
        
        Text("Натисніть ESC для повернення", self.font_small, color=TEXT_MUTED,
             shadow=True).draw(self.screen, (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 50), center=True)
        
    def draw_statistics(self):
        """Малювання екрану статистики."""
        for y in range(self.config.SCREEN_HEIGHT):
            ratio = y / self.config.SCREEN_HEIGHT
            r = int(25 * (1 + ratio * 0.5))
            g = int(30 * (1 + ratio * 0.5))
            b = int(45 * (1 + ratio * 0.5))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.config.SCREEN_WIDTH, y))
        
        title_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, 30, 400, 80,
            bg_color=PANEL_HEADER, alpha=PANEL_ALPHA,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=True
        )
        title_panel.draw(self.screen)
        Text("Статистика", self.font_large, color=TEXT_ACCENT,
             shadow=True, outline=False).draw(self.screen, (self.config.SCREEN_WIDTH // 2, 70), center=True)
        
        stats_panel = Panel(
            100, 130, self.config.SCREEN_WIDTH - 200, self.config.SCREEN_HEIGHT - 200,
            bg_color=PANEL_DARK, alpha=PANEL_ALPHA,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=True
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
            Text(f"{label}: {value}", self.font_small, color=TEXT_MUTED,
                 shadow=True).draw(self.screen, (120, y_offset))
            y_offset += 50
        
        Text("Натисніть ESC для повернення", self.font_small, color=TEXT_MUTED,
             shadow=True).draw(self.screen, (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 50), center=True)
        
    def draw_settings(self):
        """Налаштування: вертикальний список по центру."""
        self.background.draw(self.screen)
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        self.screen.blit(overlay, (0, 0))
        
        cx = self.config.SCREEN_WIDTH // 2
        h = self.config.SCREEN_HEIGHT
        
        Text("Налаштування", self.font_large, color=TEXT_ACCENT,
             shadow=True, outline=False).draw(self.screen, (cx, 55), center=True)
        
        for slider in self.settings_sliders:
            slider.draw(self.screen)
        
        for btn in self.settings_buttons:
            btn.draw(self.screen)
        
        Text("Миша: слайдери. ESC для виходу", self.font_hint, color=(120, 120, 130),
             shadow=False).draw(self.screen, (cx, h - 40), center=True)
        
    def draw_skins(self):
        """Екран вибору скінів."""
        self.background.draw(self.screen)
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        
        title_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, 30, 400, 80,
            bg_color=PANEL_HEADER, alpha=PANEL_ALPHA,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=True
        )
        title_panel.draw(self.screen)
        Text("Скіни птаха", self.font_large, color=TEXT_ACCENT,
             shadow=True, outline=False).draw(self.screen, (self.config.SCREEN_WIDTH // 2, 70), center=True)
        
        coins = self.save_data.get("statistics", {}).get("coins_collected", 0)
        Text(f"Монет: {coins}", self.font_small, color=COIN_COLOR, shadow=True).draw(self.screen, (self.config.SCREEN_WIDTH - 150, 50))
        
        unlocked = set(self.save_data.get("unlocked_skins", ["default"]))
        equipped = self.save_data.get("equipped_skin", "default")
        y_off = 140
        for sid, skin in SkinSystem.SKINS.items():
            is_unlocked = sid in unlocked
            is_equipped = sid == equipped
            c = (150, 255, 150) if is_equipped else ((200, 200, 200) if is_unlocked else (100, 100, 100))
            cost_str = "" if skin.cost == 0 else f" - {skin.cost} монет"
            status = "[Обрано]" if is_equipped else ("[Розблоковано]" if is_unlocked else f"[Заблокувати{cost_str}]")
            Text(f"{skin.name}: {status}", self.font_small, color=c, shadow=True).draw(self.screen, (120, y_off))
            y_off += 50
        for btn in self.skin_buttons:
            btn.draw(self.screen)
        
        Text("ESC - назад", self.font_tiny, color=TEXT_MUTED, shadow=True).draw(self.screen, (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 40), center=True)
    
    def setup_skins_buttons(self):
        """Створення кнопок екрану скінів."""
        unlocked = set(self.save_data.get("unlocked_skins", ["default"]))
        equipped = self.save_data.get("equipped_skin", "default")
        coins = self.save_data.get("statistics", {}).get("coins_collected", 0)
        self.skin_buttons = []
        y_off = 145
        for sid, skin in SkinSystem.SKINS.items():
            is_unlocked = sid in unlocked
            is_equipped = sid == equipped
            if is_unlocked and not is_equipped:
                btn = Button(self.config.SCREEN_WIDTH - 120, y_off, 100, 30, "Обрати", self.font_tiny,
                             (lambda s: lambda: self._equip_skin(s))(sid),
                             bg_color=SUCCESS_BG, hover_color=SUCCESS_HOVER)
                self.skin_buttons.append(btn)
            elif not is_unlocked and coins >= skin.cost:
                btn = Button(self.config.SCREEN_WIDTH - 120, y_off, 100, 30, "Купити", self.font_tiny,
                             (lambda s: lambda: self._buy_skin(s))(sid),
                             bg_color=SECONDARY_BG, hover_color=SECONDARY_HOVER)
                self.skin_buttons.append(btn)
            y_off += 50
    
    def _equip_skin(self, skin_id):
        self.save_data["equipped_skin"] = skin_id
        SaveSystem.save(self.save_data)
        self.sound_manager.play_sound('powerup')
    
    def _buy_skin(self, skin_id):
        coins = self.save_data.get("statistics", {}).get("coins_collected", 0)
        if SkinSystem.unlock(self.save_data, skin_id, coins):
            self.save_data["equipped_skin"] = skin_id
            stats = self.save_data.setdefault("statistics", {})
            stats["coins_collected"] = stats.get("coins_collected", 0) - SkinSystem.SKINS[skin_id].cost
            SaveSystem.save(self.save_data)
            self.sound_manager.play_sound('achievement')
    
    def draw_pause_menu(self):
        """Малювання меню паузи."""
        # Overlay
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        pause_panel = Panel(
            self.config.SCREEN_WIDTH // 2 - 200, self.config.SCREEN_HEIGHT // 2 - 100,
            400, 200,
            bg_color=PANEL_HEADER, alpha=PANEL_ALPHA,
            border_color=BORDER_COLOR, border_width=BORDER_WIDTH, shadow=True
        )
        pause_panel.draw(self.screen)
        Text("ПАУЗА", self.font_large, color=TEXT_ACCENT,
             shadow=True, outline=False).draw(self.screen,
            (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 - 50), center=True)
        Text("SPACE/ESC - продовжити | DOWN - dash", self.font_small, color=TEXT_MUTED,
             shadow=True).draw(self.screen,
            (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 30), center=True)
    
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
        elif self.state == 'skins':
            self.draw_skins()
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
