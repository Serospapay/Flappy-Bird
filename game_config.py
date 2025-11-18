"""
@file: game_config.py
@description: Конфігураційний файл з налаштуваннями гри (розміри, кольори, фізика).
@dependencies: -
@created: 2024-12-19
"""

class GameConfig:
    """Клас з налаштуваннями гри."""
    
    # Розміри екрану
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    # FPS
    FPS = 60
    
    # Кольори
    BG_COLOR = (135, 206, 250)  # Небесно-блакитний
    PIPE_COLOR = (34, 139, 34)  # Зелений
    PIPE_HEAD_COLOR = (0, 100, 0)  # Темно-зелений
    BIRD_COLOR = (255, 215, 0)  # Золотий
    
    # Фізика птаха
    GRAVITY = 0.6
    JUMP_STRENGTH = -10
    
    # Параметри труб
    PIPE_WIDTH = 80
    PIPE_GAP = 200  # Проміжок між трубами
    PIPE_SPEED = 4
    PIPE_SPAWN_INTERVAL = 1800  # Мілісекунди між появою нових труб
    PIPE_HEAD_HEIGHT = 40
    
    # Динамічна складність
    DIFFICULTY_SCALING = True  # Чи активна прогресивна складність
    MIN_PIPE_GAP = 150  # Мінімальний проміжок між трубами
    MIN_PIPE_SPAWN_INTERVAL = 1200  # Мінімальний інтервал між трубами

