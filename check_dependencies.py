"""
Скрипт для перевірки залежностей гри.
"""
import sys
import os

# Встановлення UTF-8 для Windows консолі
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

print(f"Python version: {sys.version.split()[0]}")
print(f"Python executable: {sys.executable}")
print()

try:
    import pygame
    print(f"[OK] pygame imported successfully: {pygame.__version__}")
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("   Try to install: pip install pygame-ce")
    sys.exit(1)

print("\nAll dependencies are installed correctly!")
print("You can run the game: python game.py")

