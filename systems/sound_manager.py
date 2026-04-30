"""
@file: sound_manager.py
@description: Менеджер звуку для гри (фонова музика та звукові ефекти).
@dependencies: pygame, numpy (optional)
@created: 2024-12-19
"""

import pygame

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class SoundManager:
    """Менеджер звуку та музики."""
    
    def __init__(self):
        """Ініціалізація менеджера звуку."""
        self.audio_available = True
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            self.audio_available = False
            print(f"Попередження: аудіо недоступне, гра працює в silent mode ({e})")
        
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_enabled = self.audio_available
        self.sfx_enabled = self.audio_available
        self._music_mood = "calm"  # calm, tension, victory
        
        # Генерація звуків програмно (якщо немає файлів)
        self.sounds = {}
        if self.audio_available:
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
        
        if not HAS_NUMPY or not self.audio_available:
            return None

        # Генерація звукової хвилі через numpy для правильного типу даних
        t = np.linspace(0, duration, frames, False)
        wave = 4096 * np.sin(2.0 * np.pi * frequency * t)
        
        # Створення стерео сигналу (2 канали)
        # Обмеження значень до int16 (-32768 до 32767)
        wave = np.clip(wave, -32767, 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        
        # Створення звуку з правильним типом даних
        return pygame.sndarray.make_sound(stereo_wave)
    
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
            if sound is None:
                return
            sound.set_volume(self.sfx_volume)
            sound.play()
    
    def set_music_mood(self, mood):
        """Dynamic music - зміна настрою (calm/tension/victory)."""
        self._music_mood = mood
    
    def play_music(self, music_data=None):
        """Відтворення фонової музики."""
        if not self.music_enabled or not self.audio_available:
            return
        pygame.mixer.music.set_volume(self.music_volume)
        
    def stop_music(self):
        """Зупинка фонової музики."""
        if not self.audio_available:
            return
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """
        Встановлення гучності музики.
        
        Args:
            volume: float - Гучність (0.0 - 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if self.audio_available:
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

