@echo off
echo Starting Extractor Service...
cd /d %~dp0
call venv\Scripts\activate.bat
cd extractor
python main.py
