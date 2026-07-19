@echo off
echo =============================================
echo   Church Website - Starting Up
echo =============================================
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Starting server...
echo Open your browser and go to: http://localhost:5000
echo Admin panel: http://localhost:5000/admin
echo Username: Eugene  ^|  Password: almighty
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
