"""
@file: sound_manager.py
@description: Менеджер звуку для гри (фонова музика та звукові ефекти).
@dependencies: pygame, math, os, numpy (optional)
@created: 2024-12-19
"""

import pygame
import math
import os

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class SoundManager:
    """Менеджер звуку та музики."""
    
    def __init__(self):
        """Ініціалізація менеджера звуку."""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_enabled = True
        self.sfx_enabled = True
        self._music_mood = "calm"  # calm, tension, victory
        
        # Генерація звуків програмно (якщо немає файлів)
        self._init_sounds()
        
    def _init_sounds(self):
        """Ініціалізація звуків (генеруємо програмно)."""
        self.sounds = {}
        
        # Звук стрибка (короткий тональний звук)
        self.sounds['jump'] = self._generate_jump_sound()
        
        # Звук колізії (низький звук)
        self.sounds['collision'] = self._generate_collision_sound()
        
        # Звук збору монети (піщаний звук)
        self.sounds['coin'] = self._generate_coin_sound()
        
        # Звук досягнення (піднесений звук)
        self.sounds['achievement'] = self._generate_achievement_sound()
        
        # Звук power-up
        self.sounds['powerup'] = self._generate_powerup_sound()
        
    def _generate_tone(self, frequency, duration, sample_rate=22050):
        """
        Генерація тонального звуку.
        
        Args:
            frequency: float - Частота звуку
            duration: float - Тривалість в секундах
            sample_rate: int - Частота дискретизації
            
        Returns:
            pygame.mixer.Sound: Звук
        """
        frames = int(duration * sample_rate)
        
        if HAS_NUMPY:
            # Генерація звукової хвилі через numpy для правильного типу даних
            t = np.linspace(0, duration, frames, False)
            wave = 4096 * np.sin(2.0 * np.pi * frequency * t)
            
            # Створення стерео сигналу (2 канали)
            # Обмеження значень до int16 (-32768 до 32767)
            wave = np.clip(wave, -32767, 32767).astype(np.int16)
            stereo_wave = np.column_stack((wave, wave))
            
            # Створення звуку з правильним типом даних
            return pygame.sndarray.make_sound(stereo_wave)
        else:
            # Fallback без numpy - використовуємо список з явним int16
            arr = []
            for i in range(frames):
                wave_value = int(4096 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                # Обмеження до int16 діапазону
                wave_value = max(-32767, min(32767, wave_value))
                arr.append([wave_value, wave_value])
            
            # Конвертація в numpy array з правильним типом (якщо доступний)
            # або використання pygame.sndarray
            sound_array = pygame.sndarray.array(arr)
            # Явна конвертація до int16 через numpy якщо доступний
            if hasattr(sound_array, 'astype'):
                sound_array = sound_array.astype('int16')
            return pygame.sndarray.make_sound(sound_array)
    
    def _generate_jump_sound(self):
        """Генерація звуку стрибка."""
        # Комбінація тонів для стрибка
        sounds = []
        for freq in [440, 550, 660]:
            sound = self._generate_tone(freq, 0.1)
            sounds.append(sound)
        
        # Простий варіант - один тон
        return self._generate_tone(550, 0.15)
    
    def _generate_collision_sound(self):
        """Генерація звуку колізії."""
        # Низький звук
        return self._generate_tone(150, 0.3)
    
    def _generate_coin_sound(self):
        """Генерація звуку збору монети."""
        # Піщаний звук
        return self._generate_tone(800, 0.2)
    
    def _generate_achievement_sound(self):
        """Генерація звуку досягнення."""
        # Піднесений звук
        return self._generate_tone(660, 0.25)
    
    def _generate_powerup_sound(self):
        """Генерація звуку power-up."""
        # Мелодійний звук
        return self._generate_tone(523, 0.2)
    
    def play_sound(self, sound_name):
        """
        Відтворення звукового ефекту.
        
        Args:
            sound_name: str - Назва звуку
        """
        if not self.sfx_enabled:
            return
            
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.sfx_volume)
            sound.play()
    
    def set_music_mood(self, mood):
        """Dynamic music - зміна настрою (calm/tension/victory)."""
        self._music_mood = mood
    
    def play_music(self, music_data=None):
        """Відтворення фонової музики."""
        if not self.music_enabled:
            return
        pygame.mixer.music.set_volume(self.music_volume)
        
    def stop_music(self):
        """Зупинка фонової музики."""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """
        Встановлення гучності музики.
        
        Args:
            volume: float - Гучність (0.0 - 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """
        Встановлення гучності звукових ефектів.
        
        Args:
            volume: float - Гучність (0.0 - 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_enabled(self, enabled):
        """
        Увімкнення/вимкнення музики.
        
        Args:
            enabled: bool - Чи увімкнено музику
        """
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()
    
    def set_sfx_enabled(self, enabled):
        """
        Увімкнення/вимкнення звукових ефектів.
        
        Args:
            enabled: bool - Чи увімкнено звукові ефекти
        """
        self.sfx_enabled = enabled

