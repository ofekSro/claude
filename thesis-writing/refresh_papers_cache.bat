@echo off
rem Deletes the extracted paper texts and extracts every PDF in Papers\ again.
rem Double-click it, or run it from any folder: it always works on the folder it sits in.
chcp 65001 >nul
setlocal
set "ROOT=%~dp0"
set "CACHE=%ROOT%.claude\cache\papers"
set "SCRIPT=%ROOT%.claude\skills\thesis-check\extract_papers.py"
if not exist "%SCRIPT%" set "SCRIPT=%USERPROFILE%\.claude\skills\thesis-check\extract_papers.py"

if not exist "%SCRIPT%" (
    echo extract_papers.py was not found in the thesis or in %USERPROFILE%\.claude\skills\thesis-check
    pause
    exit /b 1
)

echo Deleting %CACHE%
if exist "%CACHE%" rmdir /s /q "%CACHE%"

echo Extracting the papers again...
python "%SCRIPT%" "%ROOT:~0,-1%"
if errorlevel 1 (
    echo.
    echo Extraction failed. See the message above.
) else (
    echo.
    echo Done.
)
pause
