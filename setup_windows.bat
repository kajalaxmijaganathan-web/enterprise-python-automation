@echo off
setlocal
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
if errorlevel 1 (
  echo Installation failed. Check the error above.
  exit /b 1
)
echo.
echo Setup complete. Try:
echo   enterprise-report generate
echo   pytest -v
