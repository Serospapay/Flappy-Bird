@echo off
chcp 65001 >nul
title Flappy Bird - Enhanced Edition
echo ========================================
echo  Flappy Bird - Enhanced Edition
echo ========================================
echo.
echo Перевірка залежностей...

python -c "import pygame; import numpy" 2>nul
if errorlevel 1 (
    echo [ІНФОРМАЦІЯ] Встановлення залежностей...
    python -m pip install -r requirements.txt --user
    if errorlevel 1 (
        echo [ПОМИЛКА] Не вдалося встановити залежності!
        pause
        exit /b 1
    )
)

echo [ОК] Залежності встановлено!
echo.
echo Запуск гри...
echo.

python game.py

if errorlevel 1 (
    echo.
    echo [ПОМИЛКА] Помилка при запуску гри!
    pause
)

