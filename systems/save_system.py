"""
@file: save_system.py
@description: Система збереження та завантаження прогресу гравця (статистика, досягнення, налаштування).
@dependencies: json, os
@created: 2024-12-19
"""

import json
import os
from datetime import datetime

try:
    from systems.skins import SkinSystem
except ImportError:
    SkinSystem = None

class SaveSystem:
    """Клас для роботи зі збереженням даних."""
    
    SAVE_FILE = "save_data.json"
    
    DEFAULT_DATA = {
        "best_score": 0,
        "total_games": 0,
        "total_score": 0,
        "achievements": [],
        "unlocked_skins": ["default"],
        "equipped_skin": "default",
        "top_scores": [],  # Топ-5 рекордів: [{"score": int, "coins": int, "date": str}, ...]
        "settings": {
            "music_volume": 0.5,
            "sfx_volume": 0.7,
            "difficulty": "normal",
            "theme": "light"
        },
        "statistics": {
            "best_score": 0,
            "average_score": 0.0,
            "total_time_played": 0,
            "coins_collected": 0,
            "powerups_used": 0
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
                    # Валідація даних
                    if not isinstance(data, dict):
                        return SaveSystem.DEFAULT_DATA.copy()
                    
                    # Об'єднання з дефолтними даними для нових полів
                    default = SaveSystem.DEFAULT_DATA.copy()
                    default.update(data)
                    
                    # Валідація статистики
                    if "statistics" not in default or not isinstance(default["statistics"], dict):
                        default["statistics"] = SaveSystem.DEFAULT_DATA["statistics"].copy()
                    
                    # Валідація налаштувань
                    if "settings" not in default or not isinstance(default["settings"], dict):
                        default["settings"] = SaveSystem.DEFAULT_DATA["settings"].copy()
                    
                    # Валідація досягнень
                    if "achievements" not in default or not isinstance(default["achievements"], list):
                        default["achievements"] = []
                    
                    if "top_scores" not in default or not isinstance(default["top_scores"], list):
                        default["top_scores"] = []
                    if "unlocked_skins" not in default or not isinstance(default["unlocked_skins"], list):
                        default["unlocked_skins"] = ["default"]
                    if "default" not in default["unlocked_skins"]:
                        default["unlocked_skins"].insert(0, "default")
                    if SkinSystem and ("equipped_skin" not in default or default.get("equipped_skin") not in getattr(SkinSystem, "SKINS", {})):
                        default["equipped_skin"] = "default"
                    
                    return default
            except (json.JSONDecodeError, IOError, ValueError) as e:
                # Логування помилки (можна додати logging)
                print(f"Помилка завантаження збереження: {e}")
                return SaveSystem.DEFAULT_DATA.copy()
        return SaveSystem.DEFAULT_DATA.copy()
    
    @staticmethod
    def save(data):
        """
        Збереження даних з валідацією.
        
        Args:
            data: dict - Дані для збереження
        """
        if not isinstance(data, dict):
            print("Помилка: дані для збереження не є словником")
            return
        
        try:
            # Валідація основних полів перед збереженням
            validated_data = SaveSystem.DEFAULT_DATA.copy()
            validated_data.update(data)
            
            # Валідація числових значень
            if "best_score" in validated_data:
                validated_data["best_score"] = max(0, int(validated_data.get("best_score", 0)))
            
            if "total_games" in validated_data:
                validated_data["total_games"] = max(0, int(validated_data.get("total_games", 0)))
            
            if "total_score" in validated_data:
                validated_data["total_score"] = max(0, int(validated_data.get("total_score", 0)))
            
            # Валідація налаштувань
            if "settings" in validated_data and isinstance(validated_data["settings"], dict):
                settings = validated_data["settings"]
                if "music_volume" in settings:
                    settings["music_volume"] = max(0.0, min(1.0, float(settings["music_volume"])))
                if "sfx_volume" in settings:
                    settings["sfx_volume"] = max(0.0, min(1.0, float(settings["sfx_volume"])))
            
            with open(SaveSystem.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(validated_data, f, indent=2, ensure_ascii=False)
        except (IOError, ValueError, TypeError) as e:
            print(f"Помилка збереження даних: {e}")
            # Продовжуємо гру навіть якщо не вдалося зберегти
    
    @staticmethod
    def update_statistics(data, score, time_played=0, coins=0, powerups_used=0):
        """
        Оновлення статистики після гри.
        
        Args:
            data: dict - Дані збереження
            score: int - Рахунок гри
            time_played: int - Час гри в секундах
            coins: int - Зібрані монети
            powerups_used: int - Використані power-ups в цій грі
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
        
        # Оновлення використаних power-ups
        stats["powerups_used"] = stats.get("powerups_used", 0) + powerups_used
    
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

