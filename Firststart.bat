cd /d %~dp0

:: Create venv
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    goto end
)

:: Activate venv
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    goto end
)

:: Install requirements
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements.
    goto end
)

:end
echo.
set /p tmp="Press Enter to quit..."
