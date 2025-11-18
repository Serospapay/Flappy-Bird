"""
@file: save_system.py
@description: Система збереження та завантаження прогресу гравця (статистика, досягнення, налаштування).
@dependencies: json, os
@created: 2024-12-19
"""

import json
import os
from datetime import datetime

class SaveSystem:
    """Клас для роботи зі збереженням даних."""
    
    SAVE_FILE = "save_data.json"
    
    DEFAULT_DATA = {
        "best_score": 0,
        "total_games": 0,
        "total_score": 0,
        "achievements": [],
        "top_scores": [],  # Топ-5 рекордів: [{"score": int, "coins": int, "date": str}, ...]
        "settings": {
            "music_volume": 0.5,
            "sfx_volume": 0.7,
            "difficulty": "normal",
            "theme": "default"
        },
        "statistics": {
            "best_score": 0,
            "average_score": 0.0,
            "total_time_played": 0,
            "coins_collected": 0
        }
    }
    
    @staticmethod
    def load():
        """
        Завантаження даних збереження.
        
        Returns:
            dict: Дані збереження або дефолтні дані
        """
        if os.path.exists(SaveSystem.SAVE_FILE):
            try:
                with open(SaveSystem.SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Об'єднання з дефолтними даними для нових полів
                    default = SaveSystem.DEFAULT_DATA.copy()
                    default.update(data)
                    if "statistics" not in default:
                        default["statistics"] = SaveSystem.DEFAULT_DATA["statistics"].copy()
                    return default
            except (json.JSONDecodeError, IOError):
                return SaveSystem.DEFAULT_DATA.copy()
        return SaveSystem.DEFAULT_DATA.copy()
    
    @staticmethod
    def save(data):
        """
        Збереження даних.
        
        Args:
            data: dict - Дані для збереження
        """
        try:
            with open(SaveSystem.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Якщо не вдалося зберегти, продовжуємо гру
    
    @staticmethod
    def update_statistics(data, score, time_played=0, coins=0):
        """
        Оновлення статистики після гри.
        
        Args:
            data: dict - Дані збереження
            score: int - Рахунок гри
            time_played: int - Час гри в секундах
            coins: int - Зібрані монети
        """
        stats = data.setdefault("statistics", {})
        
        # Оновлення найкращого рахунку
        if score > stats.get("best_score", 0):
            stats["best_score"] = score
        if score > data.get("best_score", 0):
            data["best_score"] = score
        
        # Оновлення топ-5 рекордів
        top_scores = data.setdefault("top_scores", [])
        
        # Додати новий результат
        new_record = {
            "score": score,
            "coins": coins,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        top_scores.append(new_record)
        
        # Сортувати за рахунком (від найбільшого до найменшого)
        top_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Залишити тільки топ-5
        data["top_scores"] = top_scores[:5]
        
        # Оновлення середнього рахунку
        total_games = data.get("total_games", 0) + 1
        total_score = data.get("total_score", 0) + score
        data["total_games"] = total_games
        data["total_score"] = total_score
        
        if total_games > 0:
            stats["average_score"] = round(total_score / total_games, 2)
        
        # Оновлення загального часу
        stats["total_time_played"] = stats.get("total_time_played", 0) + time_played
        
        # Оновлення монет
        stats["coins_collected"] = stats.get("coins_collected", 0) + coins
    
    @staticmethod
    def unlock_achievement(data, achievement_id):
        """
        Розблокування досягнення.
        
        Args:
            data: dict - Дані збереження
            achievement_id: str - ID досягнення
        """
        if "achievements" not in data:
            data["achievements"] = []
        
        if achievement_id not in data["achievements"]:
            data["achievements"].append(achievement_id)
            return True  # Нове досягнення
        return False  # Вже було розблоковано

