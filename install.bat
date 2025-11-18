@echo off
chcp 65001 >nul
title Встановлення залежностей - Flappy Bird
echo ========================================
echo  Встановлення залежностей
echo  Flappy Bird - Enhanced Edition
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ПОМИЛКА] Python не знайдено!
    echo Переконайтеся, що Python встановлено і додано в PATH.
    pause
    exit /b 1
)

echo [ІНФОРМАЦІЯ] Версія Python:
python --version
echo.

echo [ІНФОРМАЦІЯ] Встановлення залежностей з requirements.txt...
python -m pip install -r requirements.txt --user

if errorlevel 1 (
    echo.
    echo [ПОМИЛКА] Не вдалося встановити залежності!
    pause
    exit /b 1
)

echo.
echo [УСПІХ] Всі залежності встановлено успішно!
echo.
echo Тепер ви можете запустити гру командою: run.bat
echo або: python game.py
echo.
pause

