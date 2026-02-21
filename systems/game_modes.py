"""
@file: game_modes.py
@description: Режими гри - Normal, Daily Challenge, Challenges.
@dependencies: datetime, random
@created: 2025-02-21
"""

from datetime import date
import random

class GameModes:
    """Система режимів гри."""
    
    MODE_NORMAL = "normal"
    MODE_DAILY = "daily"
    MODE_CHALLENGE = "challenge"
    
    CHALLENGES = {
        "one_life": {"name": "Одне життя", "desc": "Без power-ups, 1 помилка = кінець", "no_powerups": True},
        "no_jump_5": {"name": "5 без стрибка", "desc": "Пройди 5 труб не натискаючи стрибок", "max_jumps": 0, "target_score": 5},
        "speed_run": {"name": "Швидкість", "desc": "Подвійна швидкість труб", "speed_mult": 2.0},
        "narrow": {"name": "Вузькі щілини", "desc": "Проміжок між трубами -50%", "gap_mult": 0.5},
    }
    
    @staticmethod
    def get_daily_seed():
        """Seed для Daily Challenge (однаковий для всіх протягом дня)."""
        d = date.today()
        return d.year * 10000 + d.month * 100 + d.day
    
    @staticmethod
    def get_daily_random(seed=None):
        """Повертає Random з seed для daily (детермінована генерація)."""
        s = seed or GameModes.get_daily_seed()
        return random.Random(s)
    
    @staticmethod
    def get_challenge_params(challenge_id):
        return GameModes.CHALLENGES.get(challenge_id, {})
