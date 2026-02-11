@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
set PYTHONPATH=src
streamlit run scripts\app.py
pause
