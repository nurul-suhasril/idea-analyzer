@echo off
echo Starting Slack Bot...
cd /d %~dp0
call venv\Scripts\activate.bat
cd slack-bot
python app.py
