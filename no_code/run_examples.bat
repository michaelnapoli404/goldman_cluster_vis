@echo off
echo ====================================================
echo          WAVE VISUALIZER - NO CODE LAUNCHER
echo ====================================================
echo.
echo This script will automatically:
echo   1. Install conda (if needed)
echo   2. Set up the environment
echo   3. Generate 9 political visualizations
echo   4. Save results as HTML + PNG files
echo.
echo Starting Wave Visualizer Examples...
echo.

:: Check if conda is available
echo [STEP 1/6] Checking for conda installation...
echo Searching for conda in common locations...

:: Method 1: Check if conda is in PATH
where conda >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo SUCCESS: Found conda in PATH!
    goto :conda_found
)

:: Method 2: Check for Anaconda in default location
if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    echo Found Anaconda in user directory!
    set "CONDA_EXE=%USERPROFILE%\anaconda3\Scripts\conda.exe"
    set "PATH=%USERPROFILE%\anaconda3\Scripts;%PATH%"
    goto :conda_found
)

:: Method 3: Check for Miniconda in default location
if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    echo Found Miniconda in user directory!
    set "CONDA_EXE=%USERPROFILE%\miniconda3\Scripts\conda.exe"
    set "PATH=%USERPROFILE%\miniconda3\Scripts;%PATH%"
    goto :conda_found
)

:: Method 4: Check for Anaconda in ProgramData
if exist "C:\ProgramData\Anaconda3\Scripts\conda.exe" (
    echo Found Anaconda in ProgramData!
    set "CONDA_EXE=C:\ProgramData\Anaconda3\Scripts\conda.exe"
    set "PATH=C:\ProgramData\Anaconda3\Scripts;%PATH%"
    goto :conda_found
)

:: Method 5: Check for Miniconda in ProgramData
if exist "C:\ProgramData\Miniconda3\Scripts\conda.exe" (
    echo Found Miniconda in ProgramData!
    set "CONDA_EXE=C:\ProgramData\Miniconda3\Scripts\conda.exe"
    set "PATH=C:\ProgramData\Miniconda3\Scripts;%PATH%"
    goto :conda_found
)

:: If conda not found, offer automatic installation
echo.
echo ========================================================
echo CONDA NOT FOUND - AUTOMATIC INSTALLATION AVAILABLE
echo ========================================================
echo.
echo We can automatically install Miniconda for you!
echo This is safe and will not affect existing Python installations.
echo.
echo OPTION 1: Automatic Installation (Recommended)
echo   - We'll download and install Miniconda3
echo   - Takes 2-3 minutes
echo   - Completely automatic
echo.
echo OPTION 2: Manual Installation
echo   - Download from: https://docs.conda.io/en/latest/miniconda.html
echo   - Follow installation wizard
echo   - Then run this script again
echo.
set /p "INSTALL_CHOICE=Would you like us to install conda automatically? (y/n): "

if /i "%INSTALL_CHOICE%"=="y" goto :auto_install_conda
if /i "%INSTALL_CHOICE%"=="yes" goto :auto_install_conda

echo Manual installation selected.
echo Please download conda from: https://docs.conda.io/en/latest/miniconda.html
echo After installation, run this script again.
echo.
echo Press any key to exit...
pause >nul
exit /b 1

:auto_install_conda
echo.
echo [AUTO-INSTALL] Downloading and installing Miniconda3...
echo This may take a few minutes - please wait...
echo.

:: Create temp directory
set "TEMP_DIR=%TEMP%\wave_visualizer_setup"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Download Miniconda installer
echo Downloading Miniconda3 installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile '%TEMP_DIR%\miniconda_installer.exe'}"

if not exist "%TEMP_DIR%\miniconda_installer.exe" (
    echo ERROR: Failed to download Miniconda installer.
    echo Please install manually from: https://docs.conda.io/en/latest/miniconda.html
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Download complete! Installing Miniconda3...
echo.

:: Install Miniconda silently
"%TEMP_DIR%\miniconda_installer.exe" /InstallationType=JustMe /RegisterPython=0 /S /D=%USERPROFILE%\miniconda3

:: Check if installation was successful
if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    echo SUCCESS: Miniconda3 installed successfully!
    set "CONDA_EXE=%USERPROFILE%\miniconda3\Scripts\conda.exe"
    set "PATH=%USERPROFILE%\miniconda3\Scripts;%PATH%"
    
    :: Clean up installer
    del "%TEMP_DIR%\miniconda_installer.exe" >nul 2>&1
    rmdir "%TEMP_DIR%" >nul 2>&1
    
    goto :conda_found
) else (
    echo ERROR: Installation may have failed.
    echo Please try manual installation from: https://docs.conda.io/en/latest/miniconda.html
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:conda_found
echo SUCCESS: Conda found and configured!

:: Initialize conda for batch usage
echo [STEP 2/6] Initializing conda for batch usage...
call conda.bat init cmd.exe >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: conda.bat init failed, trying alternative...
    call conda init cmd.exe >nul 2>&1
)
echo SUCCESS: Conda initialized!

:: Check if goldman_env environment exists
echo [STEP 3/6] Checking for goldman_env environment...
conda info --envs | findstr "goldman_env" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: goldman_env environment not found.
    echo Creating environment from environment.yml...
    echo.
    
    :: Navigate to parent directory where environment.yml should be
    cd ..
    echo Current directory: %CD%
    
    :: Check if environment.yml exists
    if not exist "environment.yml" (
        echo ERROR: environment.yml not found in project directory.
        echo Expected location: %CD%\environment.yml
        echo Make sure you're running this from the correct no_code folder.
        echo.
        echo Directory contents:
        dir /b
        pause
        exit /b 1
    )
    
    :: Create the environment
    echo Creating conda environment... This may take a few minutes.
    echo Please wait...
    call conda env create -f environment.yml
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create conda environment.
        echo Please check that environment.yml is valid and try again.
        pause
        exit /b 1
    )
    
    echo SUCCESS: goldman_env environment created!
    echo.
    
    :: Go back to no_code directory
    cd no_code
) else (
    echo SUCCESS: goldman_env environment found!
)

:: Try alternative conda activation methods
echo [STEP 4/6] Activating goldman_env conda environment...

:: Method 1: Standard conda.bat activate
CALL conda.bat activate goldman_env >nul 2>&1
if %ERRORLEVEL% equ 0 goto :activation_success

:: Method 2: Try regular conda activate
call conda activate goldman_env >nul 2>&1
if %ERRORLEVEL% equ 0 goto :activation_success

:: Method 3: Try with full conda command
"%CONDA_EXE%" activate goldman_env >nul 2>&1
if %ERRORLEVEL% equ 0 goto :activation_success

:: All methods failed
echo ERROR: Failed to activate goldman_env environment.
echo.
echo Please try these manual steps:
echo 1. Open a new command prompt
echo 2. Run: conda activate goldman_env
echo 3. Run: python example_visualizations/political_w1_w3.py
echo.
pause
exit /b 1

:activation_success
echo SUCCESS: goldman_env environment activated!

:: Navigate to project root first (where pyproject.toml is located)
cd ..

:: Install the wave_visualizer package in editable mode
echo [STEP 5/7] Installing wave_visualizer package...
pip install -e .
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to install wave_visualizer package.
    echo This might cause import errors in the examples.
    echo.
) else (
    echo SUCCESS: wave_visualizer package installed!
)

:: We're already in project root now
echo [STEP 6/7] Checking project directory...

:: Check if example_visualizations exists
if not exist "example_visualizations" (
    echo ERROR: example_visualizations folder not found.
    echo Current directory: %CD%
    echo Make sure you're running this from the correct location.
    pause
    exit /b 1
)
echo SUCCESS: Found example_visualizations folder!

:: Run all Python files in example_visualizations
echo [STEP 7/7] Running example visualizations...
echo.

set SUCCESS_COUNT=0
set TOTAL_COUNT=0

for %%f in (example_visualizations\*.py) do (
    set /a TOTAL_COUNT+=1
    echo.
    echo ================================================
    echo Running %%f...
    echo ================================================
    python "%%f"
    if %ERRORLEVEL% neq 0 (
        echo.
        echo WARNING: %%f failed with error code %ERRORLEVEL%
    ) else (
        echo.
        echo SUCCESS: %%f completed successfully!
        set /a SUCCESS_COUNT+=1
    )
)

echo.
echo ================================================================
echo ALL EXAMPLES COMPLETED!
echo ================================================================
echo.
echo Summary:
echo - Successfully ran %SUCCESS_COUNT% out of %TOTAL_COUNT% visualization scripts
echo - Results saved to: example_visualizations/exports/
echo.
echo What you'll find in the exports folder:
echo - .html files = Interactive charts (open in web browser)
echo - .png files = High-resolution images (for presentations)
echo.
echo TIP: Navigate to example_visualizations/exports/ to see your visualizations!
echo.
echo Press any key to exit...
pause >nul 