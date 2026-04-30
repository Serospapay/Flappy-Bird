@echo off
chcp 65001 >nul
title Flappy Bird - Enhanced Edition
echo ========================================
echo  Flappy Bird - Enhanced Edition
echo ========================================
echo.
echo Перевірка залежностей...

where py >nul 2>&1
if errorlevel 1 (
    set "PY_CMD=python"
) else (
    set "PY_CMD=py -3"
)

%PY_CMD% -c "import pygame; import numpy" 2>nul
if errorlevel 1 (
    echo [ІНФОРМАЦІЯ] Встановлення залежностей...
    %PY_CMD% -m pip install -r requirements.txt --user
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

%PY_CMD% -m src.game

if errorlevel 1 (
    echo.
    echo [ПОМИЛКА] Помилка при запуску гри!
    pause
)

