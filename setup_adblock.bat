
@echo off
setlocal
echo KakaoTalk AdBlocker Setup Starting...

:: 1. Copy Python script to a permanent location
set "TARGET_DIR=%USERPROFILE%\KakaoAdBlock"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
set "SCRIPT_PATH=%TARGET_DIR%\kakaotalk_adblock.py"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\KakaoAdBlock.lnk"

echo.
echo Stopping old ad blocker process if it is running...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*KakaoAdBlock*kakaotalk_adblock.py*' } | ForEach-Object { Invoke-CimMethod -InputObject $_ -MethodName Terminate | Out-Null }"

copy /Y "kakaotalk_adblock.py" "%TARGET_DIR%\"

:: 2. Create Startup Shortcut
powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '%SCRIPT_PATH%'; $Shortcut.WindowStyle = 7; $Shortcut.Save()"

echo.
echo [OK] Startup shortcut created.
echo [OK] Starting updated ad blocker now.
start "" pythonw.exe "%SCRIPT_PATH%"
echo.
echo -----------------------------------------------------------
echo [IMPORTANT] Please run Notepad as Administrator and add the 
echo domains in 'hosts_entries.txt' to C:\Windows\System32\drivers\etc\hosts
echo -----------------------------------------------------------
echo.
echo Setup Complete! The ad blocker will run automatically on startup.
pause
