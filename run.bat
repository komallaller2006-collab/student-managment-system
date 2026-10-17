@echo off
title Student Management System
echo ===============================================================
echo     Starting Student Management System
echo ===============================================================
echo.
echo Opening browser to: http://localhost:5000
echo Default Admin Credentials: admin / admin123
echo.
start http://localhost:5000

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe app.py
) else (
    python app.py
)

pause
