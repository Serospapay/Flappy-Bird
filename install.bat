@echo off
chcp 65001 >nul
title Встановлення залежностей - Flappy Bird
echo ========================================
echo  Встановлення залежностей
echo  Flappy Bird - Enhanced Edition
echo ========================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    set "PY_CMD=python"
) else (
    set "PY_CMD=py -3"
)

%PY_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ПОМИЛКА] Python не знайдено!
    echo Переконайтеся, що Python встановлено і додано в PATH.
    pause
    exit /b 1
)

echo [ІНФОРМАЦІЯ] Версія Python:
%PY_CMD% --version
echo.

echo [ІНФОРМАЦІЯ] Встановлення залежностей з requirements.txt...
%PY_CMD% -m pip install -r requirements.txt --user

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
echo або: py -3 -m src.game
echo.
pause

