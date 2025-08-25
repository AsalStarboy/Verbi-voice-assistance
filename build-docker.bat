@echo off
REM Build script for Verbi Voice Assistant Docker (Windows)

echo 🏗️ Building Verbi Voice Assistant Docker Image...

REM Build the Docker image
docker build -t verbi-voice-assistant:latest .

if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully!
    echo 📦 Image: verbi-voice-assistant:latest
    echo.
    echo 🚀 To run the voice assistant:
    echo    docker-compose -f docker-compose.windows.yml up
) else (
    echo ❌ Docker build failed!
    exit /b 1
)
