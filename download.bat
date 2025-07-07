@echo off
setlocal ENABLEDELAYEDEXPANSION
set TFLITE_DISABLE_XNNPACK=1
echo Logged-in user: %USERNAME%

:: Step 1: Top-level menu
echo.
echo Choose a category to run:
echo 1. Hotels
echo 2. Stocks
set /p processFor="Enter your choice (1-2): "

:: Step 2: Show sub-options based on processFor
if "%processFor%"=="1" (
    echo.
    echo Choose Hotel Option:
    echo 1. ITC Kohinur
    echo 2. ITC Sonar
    echo 3. ALL
    set /p processFor2="Enter your choice (1-3): "
) else if "%processFor%"=="2" (
    echo.
    echo Choose Stock Option:
    echo 1. ITC
    echo 2. TATA
    echo 3. ALL
    set /p processFor2="Enter your choice (1-3): "
) else (
    set processFor2=3
)

:: Step 3: Show sub-options based on processFor
echo.
echo Choose a back date ranges to run:
set /p processFor3="Enter how many days ago you want to check (e.g. 2, 3, 4): "

:: Step 4: Run Python script with both values
"%~dp0clean_env\Scripts\python.exe" -B "%~dp0wrapperWebScrap.py" %processFor% %processFor2% %processFor3%

pause
