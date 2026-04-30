"""
@file: difficulty_manager.py
@description: Менеджер динамічної складності - прогресивне ускладнення гри з ростом рахунку.
@dependencies: game_config
@created: 2024-12-19
"""

from src.pipe import Pipe

class DifficultyManager:
    """Менеджер динамічної складності."""
    
    def __init__(self, config):
        """
        Ініціалізація менеджера складності.
        
        Args:
            config: GameConfig - Конфігурація гри
        """
        self.config = config
        self.base_gap = config.PIPE_GAP
        self.base_speed = config.PIPE_SPEED
        self.base_spawn_interval = config.PIPE_SPAWN_INTERVAL
        
    def get_difficulty_params(self, score):
        """
        Отримання параметрів складності в залежності від рахунку.
        
        Args:
            score: int - Поточний рахунок
            
        Returns:
            dict: Параметри складності (gap, speed, spawn_interval)
        """
        if not self.config.DIFFICULTY_SCALING:
            return {
                'gap': self.base_gap,
                'speed': self.base_speed,
                'spawn_interval': self.base_spawn_interval
            }
        
        # Прогресивне ускладнення
        # Кожні 10 очок зменшуємо проміжок та інтервал, збільшуємо швидкість
        difficulty_level = score // 10
        
        # Зменшення проміжку (мінімум 150)
        gap = max(
            self.config.MIN_PIPE_GAP,
            self.base_gap - (difficulty_level * 10)
        )
        
        # Збільшення швидкості (максимум 8)
        speed = min(
            8.0,
            self.base_speed + (difficulty_level * 0.5)
        )
        
        # Зменшення інтервалу між трубами (мінімум 1200 мс)
        spawn_interval = max(
            self.config.MIN_PIPE_SPAWN_INTERVAL,
            self.base_spawn_interval - (difficulty_level * 100)
        )
        
        return {
            'gap': gap,
            'speed': speed,
            'spawn_interval': spawn_interval
        }
    
    def apply_difficulty(self, pipe_manager, score):
        """
        Застосування складності до менеджера труб.
        
        Args:
            pipe_manager: PipeManager - Менеджер труб
            score: int - Поточний рахунок
        """
        params = self.get_difficulty_params(score)
        
        # Оновлення параметрів труб
        self.config.PIPE_GAP = params['gap']
        self.config.PIPE_SPEED = params['speed']
        self.config.PIPE_SPAWN_INTERVAL = params['spawn_interval']
        
        # Оновлення параметрів існуючих труб (крім SHRINKING - вони зменшуються самостійно)
        for pipe in pipe_manager.pipes:
            if pipe.type != Pipe.TYPE_SHRINKING:
                pipe.gap_size = params['gap']
            pipe.config.PIPE_SPEED = params['speed']

