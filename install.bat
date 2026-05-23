@echo off
setlocal enabledelayedexpansion

set VERSION=1.0.0
set INSTALL_DIR=%USERPROFILE%\.keytrace
set SCRIPT_DIR=%~dp0

echo.
echo  KEYTRACE v%VERSION% -- Windows Installer
echo.
echo  This installer will:
echo  - Check your Python version
echo  - Install PyQt6
echo  - Install KeyTrace to %INSTALL_DIR%
echo  - Create a desktop shortcut
echo.
pause

echo.
echo -- Step 1: Checking Python
echo.

set PYTHON=
for %%P in (python python3) do (
    %%P --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON=%%P
    )
)

if "%PYTHON%"=="" (
    echo [ERR] Python not found.
    echo       Download from: https://www.python.org/downloads/
    echo       Check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [OK] Python found

echo.
echo -- Step 2: Installing PyQt6
echo.

%PYTHON% -m pip install PyQt6 -q
if %errorlevel% neq 0 (
    echo [ERR] Failed to install PyQt6. Try: pip install PyQt6
    pause
    exit /b 1
)
echo [OK] PyQt6 installed

where tshark >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] tshark found
) else (
    echo [WARN] tshark not found. Download from https://www.wireshark.org/download.html
)

echo.
echo -- Step 3: Installing KeyTrace
echo.

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\core\commands" mkdir "%INSTALL_DIR%\core\commands"
if not exist "%INSTALL_DIR%\assets" mkdir "%INSTALL_DIR%\assets"

for %%F in (gui.py main.py browser_launcher.py start_keytrace.py decryptor.py requirements.txt) do (
    if exist "%SCRIPT_DIR%%%F" (
        copy /Y "%SCRIPT_DIR%%%F" "%INSTALL_DIR%\%%F" >nul
        echo [OK] Copied %%F
    ) else (
        echo [WARN] Missing: %%F
    )
)

if exist "%SCRIPT_DIR%core" (
    xcopy /E /Y /Q "%SCRIPT_DIR%core" "%INSTALL_DIR%\core\" >nul
    echo [OK] Copied core\
)

if exist "%SCRIPT_DIR%assets" (
    xcopy /E /Y /Q "%SCRIPT_DIR%assets" "%INSTALL_DIR%\assets\" >nul
    echo [OK] Copied assets\
)

echo.
echo -- Step 4: Setting SSLKEYLOGFILE
echo.

set KEYLOG_PATH=%USERPROFILE%\keytrace_sslkeylogfile.txt
setx SSLKEYLOGFILE "%KEYLOG_PATH%" >nul 2>&1
echo [OK] SSLKEYLOGFILE configured

echo.
echo -- Step 5: Desktop shortcut
echo.

set SHORTCUT=%USERPROFILE%\Desktop\KeyTrace.lnk
set VBS=%TEMP%\create_shortcut.vbs

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo sLinkFile = "%SHORTCUT%" >> "%VBS%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS%"
echo oLink.TargetPath = "%PYTHON%" >> "%VBS%"
echo oLink.Arguments = "%INSTALL_DIR%\gui.py" >> "%VBS%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%VBS%"
echo oLink.Description = "KeyTrace TLS Decryption Tool" >> "%VBS%"
echo oLink.Save >> "%VBS%"

cscript //nologo "%VBS%"
del "%VBS%"
echo [OK] Desktop shortcut created

echo.
echo -----------------------------------------
echo   KeyTrace v%VERSION% installed successfully!
echo -----------------------------------------
echo.
echo   Launch: double-click KeyTrace on Desktop
echo   Or run: %PYTHON% %INSTALL_DIR%\gui.py
echo.
pause
