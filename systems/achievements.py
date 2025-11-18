"""
@file: achievements.py
@description: Система досягнень (achievements) для гри.
@dependencies: -
@created: 2024-12-19
"""

class Achievement:
    """Клас одного досягнення."""
    
    def __init__(self, achievement_id, name, description, icon=""):
        """
        Ініціалізація досягнення.
        
        Args:
            achievement_id: str - Унікальний ID досягнення
            name: str - Назва досягнення
            description: str - Опис досягнення
            icon: str - Іконка (опціонально)
        """
        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.icon = icon

class AchievementSystem:
    """Система досягнень."""
    
    ACHIEVEMENTS = {
        "first_score": Achievement(
            "first_score",
            "Перші кроки",
            "Набери перший рахунок"
        ),
        "score_10": Achievement(
            "score_10",
            "Десятка",
            "Набери 10 очок"
        ),
        "score_25": Achievement(
            "score_25",
            "Чверть сотні",
            "Набери 25 очок"
        ),
        "score_50": Achievement(
            "score_50",
            "Пів сотні",
            "Набери 50 очок"
        ),
        "score_100": Achievement(
            "score_100",
            "Сотня!",
            "Набери 100 очок"
        ),
        "collect_10_coins": Achievement(
            "collect_10_coins",
            "Колекціонер",
            "Збери 10 монет"
        ),
        "collect_50_coins": Achievement(
            "collect_50_coins",
            "Скарбничка",
            "Збери 50 монет"
        ),
        "use_powerup": Achievement(
            "use_powerup",
            "Сила!",
            "Використай power-up"
        ),
        "perfect_10": Achievement(
            "perfect_10",
            "Ідеальна десятка",
            "Пройди 10 труб без зіткнень"
        ),
        "survivor": Achievement(
            "survivor",
            "Вижив",
            "Зіграй 10 ігор"
        )
    }
    
    @staticmethod
    def check_achievements(game_state, unlocked_achievements):
        """
        Перевірка досягнень на основі ігрового стану.
        
        Args:
            game_state: dict - Поточний стан гри (score, coins, etc.)
            unlocked_achievements: list - Список розблокованих досягнень
            
        Returns:
            list: Список нових досягнень, що були розблоковані
        """
        new_achievements = []
        score = game_state.get("score", 0)
        coins = game_state.get("coins_collected", 0)
        powerups_used = game_state.get("powerups_used", 0)
        perfect_run = game_state.get("perfect_run", 0)
        total_games = game_state.get("total_games", 0)
        
        # Перевірка досягнень по рахунку
        if score >= 1 and "first_score" not in unlocked_achievements:
            new_achievements.append("first_score")
        if score >= 10 and "score_10" not in unlocked_achievements:
            new_achievements.append("score_10")
        if score >= 25 and "score_25" not in unlocked_achievements:
            new_achievements.append("score_25")
        if score >= 50 and "score_50" not in unlocked_achievements:
            new_achievements.append("score_50")
        if score >= 100 and "score_100" not in unlocked_achievements:
            new_achievements.append("score_100")
        
        # Перевірка досягнень по монетам
        if coins >= 10 and "collect_10_coins" not in unlocked_achievements:
            new_achievements.append("collect_10_coins")
        if coins >= 50 and "collect_50_coins" not in unlocked_achievements:
            new_achievements.append("collect_50_coins")
        
        # Перевірка досягнень по power-ups
        if powerups_used > 0 and "use_powerup" not in unlocked_achievements:
            new_achievements.append("use_powerup")
        
        # Перевірка досягнень по ідеальній грі
        if perfect_run >= 10 and "perfect_10" not in unlocked_achievements:
            new_achievements.append("perfect_10")
        
        # Перевірка досягнень по кількості ігор
        if total_games >= 10 and "survivor" not in unlocked_achievements:
            new_achievements.append("survivor")
        
        return new_achievements
    
    @staticmethod
    def get_achievement(achievement_id):
        """
        Отримання досягнення за ID.
        
        Args:
            achievement_id: str - ID досягнення
            
        Returns:
            Achievement або None
        """
        return AchievementSystem.ACHIEVEMENTS.get(achievement_id)

