"""
@file: skins.py
@description: Система скінів птаха. Розблоковка через монети.
@dependencies: -
@created: 2025-02-21
"""

class BirdSkin:
    """Один скін птаха."""
    
    def __init__(self, skin_id, name, cost, colors):
        """
        Args:
            skin_id: str - ID скіна
            name: str - Назва
            cost: int - Вартість в монетах (0 = безкоштовний)
            colors: tuple - (основний, світлий, темний, акцент) RGB
        """
        self.skin_id = skin_id
        self.name = name
        self.cost = cost
        self.colors = colors  # (body_main, body_light, body_dark, accent)


class SkinSystem:
    """Система скінів."""
    
    SKINS = {
        "default": BirdSkin("default", "Класичний", 0, 
            ((255, 220, 100), (255, 240, 180), (255, 180, 30), (255, 200, 50))),
        "fire": BirdSkin("fire", "Вогняний", 50,
            ((255, 100, 50), (255, 200, 150), (200, 50, 0), (255, 150, 50))),
        "ice": BirdSkin("ice", "Крижаний", 50,
            ((150, 220, 255), (220, 245, 255), (80, 180, 220), (100, 200, 255))),
        "forest": BirdSkin("forest", "Лісовий", 75,
            ((80, 180, 80), (150, 220, 150), (40, 120, 40), (100, 200, 100))),
        "royal": BirdSkin("royal", "Королівський", 100,
            ((180, 100, 255), (220, 180, 255), (120, 50, 200), (200, 150, 255))),
        "midnight": BirdSkin("midnight", "Північний", 100,
            ((60, 60, 120), (120, 120, 180), (30, 30, 80), (80, 80, 200))),
    }
    
    DEFAULT_SKIN = "default"
    
    @staticmethod
    def get_skin(skin_id):
        return SkinSystem.SKINS.get(skin_id, SkinSystem.SKINS["default"])
    
    @staticmethod
    def get_colors(skin_id):
        skin = SkinSystem.get_skin(skin_id)
        return skin.colors
    
    @staticmethod
    def can_unlock(skin_id, coins):
        skin = SkinSystem.SKINS.get(skin_id)
        return skin and skin.cost > 0 and coins >= skin.cost
    
    @staticmethod
    def unlock(data, skin_id, coins):
        if skin_id in data.get("unlocked_skins", []):
            return False
        skin = SkinSystem.SKINS.get(skin_id)
        if not skin or skin.cost <= 0 or coins < skin.cost:
            return False
        total = data.get("statistics", {}).get("coins_collected", 0)
        if total < skin.cost:
            return False
        data.setdefault("unlocked_skins", []).append(skin_id)
        return True
