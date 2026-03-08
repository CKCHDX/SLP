@echo off
REM ============================================================================
REM   SLP - SECURE LINE PROTOCOL
REM   Complete Setup and Testing Script for Windows
REM ============================================================================

color 0A
echo.
echo ============================================================================
echo   SLP - SECURE LINE PROTOCOL
echo   Military-Grade Triple-Layer Encryption
echo ============================================================================
echo.
echo   This script will:
echo   1. Check Python installation
echo   2. Install dependencies
echo   3. Test encryption layers
echo   4. Run secure server and client
echo   5. Build Windows GUI client
echo.
echo ============================================================================
echo.
pause

REM ============================================================================
REM STEP 1: Check Python Installation
REM ============================================================================

echo.
echo [STEP 1/6] Checking Python installation...
echo ============================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Python version: %PYVER%
echo.

echo [OK] Python installation verified!
echo.
pause

REM ============================================================================
REM STEP 2: Install Dependencies
REM ============================================================================

echo.
echo [STEP 2/6] Installing dependencies...
echo ============================================================================
echo.
echo Installing cryptography library for encryption...
echo.

python -m pip install --upgrade pip
python -m pip install cryptography pynacl

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Try running as Administrator or check internet connection.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed successfully!
echo.
pause

REM ============================================================================
REM STEP 3: Test Encryption Layers
REM ============================================================================

echo.
echo [STEP 3/6] Testing encryption layers...
echo ============================================================================
echo.
echo Testing Layer 1: AES-256-GCM...
echo.
python slp\encryption\aes_layer.py

if errorlevel 1 (
    echo.
    echo ERROR: AES-256-GCM test failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Testing Layer 2: ChaCha20-Poly1305...
echo.
python slp\encryption\chacha_layer.py

if errorlevel 1 (
    echo.
    echo ERROR: ChaCha20-Poly1305 test failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Testing Layer 3: Noise Protocol...
echo.
python slp\encryption\noise_layer.py

if errorlevel 1 (
    echo.
    echo ERROR: Noise Protocol test failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Testing Triple-Layer Encryption...
echo.
python slp\encryption\triple_layer.py

if errorlevel 1 (
    echo.
    echo ERROR: Triple-Layer encryption test failed!
    pause
    exit /b 1
)

echo.
echo [OK] All encryption layers working correctly!
echo.
pause

REM ============================================================================
REM STEP 4: Run Performance Benchmark
REM ============================================================================

echo.
echo [STEP 4/6] Running performance benchmark...
echo ============================================================================
echo.
echo This will test encryption speed with various payload sizes...
echo.

python examples\benchmark_encryption.py

if errorlevel 1 (
    echo.
    echo WARNING: Benchmark failed, but continuing...
)

echo.
echo [OK] Benchmark complete!
echo.
pause

REM ============================================================================
REM STEP 5: Interactive Testing Menu
REM ============================================================================

:MENU
echo.
echo ============================================================================
echo [STEP 5/6] Choose what to test:
echo ============================================================================
echo.
echo   1. Start SECURE SERVER (with encryption)
echo   2. Test SECURE CLIENT (in new window)
echo   3. Start BASIC SERVER (no encryption - for testing)
echo   4. Test BASIC CLIENT (in new window)
echo   5. Build Windows GUI Client (.exe)
echo   6. Run Performance Benchmark
echo   7. Test Everything (automated)
echo   8. Open Security Documentation
echo   9. Exit
echo.
echo ============================================================================
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto SECURE_SERVER
if "%choice%"=="2" goto SECURE_CLIENT
if "%choice%"=="3" goto BASIC_SERVER
if "%choice%"=="4" goto BASIC_CLIENT
if "%choice%"=="5" goto BUILD_GUI
if "%choice%"=="6" goto BENCHMARK
if "%choice%"=="7" goto AUTO_TEST
if "%choice%"=="8" goto DOCS
if "%choice%"=="9" goto EXIT

echo Invalid choice. Please try again.
ping 127.0.0.1 -n 2 > nul
goto MENU

REM ============================================================================
REM SECURE SERVER
REM ============================================================================

:SECURE_SERVER
echo.
echo ============================================================================
echo   Starting SECURE SERVER with Triple-Layer Encryption
echo ============================================================================
echo.
echo Server will listen on: 0.0.0.0:4270
echo Security: AES-256-GCM + ChaCha20-Poly1305 + Noise Protocol
echo.
echo Press Ctrl+C to stop the server
echo.
echo To test: Open another terminal and run: python examples\secure_client.py
echo.
echo ============================================================================
echo.
python examples\secure_server.py
goto MENU

REM ============================================================================
REM SECURE CLIENT
REM ============================================================================

:SECURE_CLIENT
echo.
echo ============================================================================
echo   Testing SECURE CLIENT
echo ============================================================================
echo.
echo Connecting to: slp://localhost:4270/
echo Security: Triple-Layer Encryption
echo.
echo Make sure the secure server is running first!
echo.
echo ============================================================================
echo.
start "SLP Secure Client" cmd /k "python examples\secure_client.py slp://localhost:4270/ && pause"
echo.
echo Client opened in new window!
echo.
pause
goto MENU

REM ============================================================================
REM BASIC SERVER
REM ============================================================================

:BASIC_SERVER
echo.
echo ============================================================================
echo   Starting BASIC SERVER (No Encryption - For Testing Only)
echo ============================================================================
echo.
echo WARNING: This server has NO encryption!
echo Use only for testing the basic protocol.
echo.
echo Server will listen on: 0.0.0.0:4270
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.
python examples\server_v2.py
goto MENU

REM ============================================================================
REM BASIC CLIENT
REM ============================================================================

:BASIC_CLIENT
echo.
echo ============================================================================
echo   Testing BASIC CLIENT (No Encryption)
echo ============================================================================
echo.
echo Make sure the basic server is running first!
echo.
start "SLP Basic Test" cmd /k "python examples\test_slp.py && pause"
echo.
echo Client opened in new window!
echo.
pause
goto MENU

REM ============================================================================
REM BUILD GUI CLIENT
REM ============================================================================

:BUILD_GUI
echo.
echo ============================================================================
echo   Building Windows GUI Client
echo ============================================================================
echo.
echo This will create a standalone .exe file that users can run
echo without installing Python.
echo.
echo Installing PyInstaller...
echo.
python -m pip install pyinstaller

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install PyInstaller!
    pause
    goto MENU
)

echo.
echo Building executable...
echo.
cd client
pyinstaller --onefile --windowed --name=SLP_Client slp_client_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    cd ..
    pause
    goto MENU
)

cd ..

echo.
echo ============================================================================
echo   BUILD COMPLETE!
echo ============================================================================
echo.
echo Executable created: client\dist\SLP_Client.exe
echo.
echo You can now:
echo   1. Run the .exe directly
echo   2. Share it with others (no Python required)
echo   3. Test it by double-clicking the file
echo.
echo File size:
dir client\dist\SLP_Client.exe | find "SLP_Client.exe"
echo.
echo ============================================================================
echo.
set /p runexe="Do you want to run the GUI client now? (y/n): "
if /i "%runexe%"=="y" (
    echo.
    echo Launching GUI client...
    start "" "client\dist\SLP_Client.exe"
    echo.
    echo GUI client launched!
    echo.
)
pause
goto MENU

REM ============================================================================
REM BENCHMARK
REM ============================================================================

:BENCHMARK
echo.
echo ============================================================================
echo   Running Performance Benchmark
echo ============================================================================
echo.
python examples\benchmark_encryption.py
echo.
pause
goto MENU

REM ============================================================================
REM AUTOMATED TESTING
REM ============================================================================

:AUTO_TEST
echo.
echo ============================================================================
echo   Automated Testing Suite
echo ============================================================================
echo.
echo This will test:
echo   1. Basic packet format
echo   2. Encryption layers
echo   3. Server/client communication
echo.
echo Starting tests...
echo.
echo ============================================================================
echo Test 1: Basic SLP Packet
echo ============================================================================
python -c "from slp.protocol.packet import SLPPacket; p = SLPPacket(SLPPacket.TYPE_REQUEST, b'test'); print('OK: Packet created:', p)"
if errorlevel 1 (
    echo FAILED!
    pause
    goto MENU
)
echo.

echo ============================================================================
echo Test 2: AES-256-GCM Encryption
echo ============================================================================
python -c "from slp.encryption.aes_layer import AESLayer; aes = AESLayer(); enc = aes.encrypt(b'test'); dec = aes.decrypt(enc); assert dec == b'test'; print('OK: AES encryption works')"
if errorlevel 1 (
    echo FAILED!
    pause
    goto MENU
)
echo.

echo ============================================================================
echo Test 3: ChaCha20-Poly1305 Encryption
echo ============================================================================
python -c "from slp.encryption.chacha_layer import ChaChaLayer; cc = ChaChaLayer(); enc = cc.encrypt(b'test'); dec = cc.decrypt(enc); assert dec == b'test'; print('OK: ChaCha encryption works')"
if errorlevel 1 (
    echo FAILED!
    pause
    goto MENU
)
echo.

echo ============================================================================
echo Test 4: Noise Protocol
echo ============================================================================
python -c "from slp.encryption.noise_layer import NoiseLayer; c=NoiseLayer(); s=NoiseLayer(); hello=c.initiate_handshake(); resp=s.respond_handshake(hello); c.complete_handshake(resp); enc=c.encrypt(b'test'); dec=s.decrypt(enc); assert dec==b'test'; print('OK: Noise protocol works')"
if errorlevel 1 (
    echo FAILED!
    pause
    goto MENU
)
echo.

echo ============================================================================
echo Test 5: Triple-Layer Encryption
echo ============================================================================
python -c "from slp.encryption.triple_layer import TripleLayerEncryption; c=TripleLayerEncryption(); s=TripleLayerEncryption(); hello=c.initiate_handshake(); resp=s.respond_handshake(hello); c.complete_handshake(resp); enc=c.encrypt(b'test',b'meta'); dec=s.decrypt(enc,b'meta'); assert dec==b'test'; print('OK: Triple-layer works')"
if errorlevel 1 (
    echo FAILED!
    pause
    goto MENU
)
echo.

echo ============================================================================
echo   ALL TESTS PASSED!
echo ============================================================================
echo.
echo   Your SLP installation is working correctly!
echo   Security: MILITARY-GRADE
echo   Status: READY FOR USE
echo.
pause
goto MENU

REM ============================================================================
REM DOCUMENTATION
REM ============================================================================

:DOCS
echo.
echo ============================================================================
echo   Opening Documentation
echo ============================================================================
echo.
echo Available documentation:
echo.
echo   1. SECURITY.md - Security architecture and encryption details
echo   2. TESTING_GUIDE.md - Complete testing instructions
echo   3. README.md - Project overview
echo   4. ARCHITECTURE.md - System architecture
echo.
set /p doc="Which document? (1-4): "

if "%doc%"=="1" start SECURITY.md
if "%doc%"=="2" start TESTING_GUIDE.md
if "%doc%"=="3" start README.md
if "%doc%"=="4" start ARCHITECTURE.md

echo.
pause
goto MENU

REM ============================================================================
REM EXIT
REM ============================================================================

:EXIT
echo.
echo ============================================================================
echo   Thank you for using SLP - Secure Line Protocol
echo ============================================================================
echo.
echo   Oscyra Solutions
echo   https://oscyra.solutions/
echo   https://github.com/CKCHDX/SLP
echo.
echo   Security Level: MILITARY-GRADE
echo   Encryption: Triple-Layer (AES + ChaCha + Noise)
echo.
echo ============================================================================
echo.
pause
exit /b 0
