@echo off
REM Adobe Hackathon Docker Build Script for Windows
REM Provides optimized build options for different use cases

echo 🐳 Adobe Hackathon Docker Build Script
echo ==========================================

set BUILD_TYPE=%1
set CACHE_OPTION=%2

if "%BUILD_TYPE%"=="" set BUILD_TYPE=dev
if "%CACHE_OPTION%"=="" set CACHE_OPTION=--no-cache

if "%BUILD_TYPE%"=="dev" goto :build_dev
if "%BUILD_TYPE%"=="development" goto :build_dev
if "%BUILD_TYPE%"=="prod" goto :build_prod
if "%BUILD_TYPE%"=="production" goto :build_prod
if "%BUILD_TYPE%"=="both" goto :build_both
if "%BUILD_TYPE%"=="compose" goto :build_compose
if "%BUILD_TYPE%"=="clean" goto :clean
goto :usage

:build_dev
echo Building development image (fast, minimal dependencies)...
docker build %CACHE_OPTION% -f dockerfile.dev -t adobe-hackathon:dev .
if %ERRORLEVEL% EQU 0 (
    echo ✅ Development image built successfully!
    echo ⚠️  Run with: docker run -v "%cd%\output_1A:/app/output_1A" adobe-hackathon:dev
) else (
    echo ❌ Build failed!
    exit /b 1
)
goto :end

:build_prod
echo Building production image (full functionality)...
docker build %CACHE_OPTION% -f dockerfile -t adobe-hackathon:prod .
if %ERRORLEVEL% EQU 0 (
    echo ✅ Production image built successfully!
    echo ⚠️  Run with: docker run -v "%cd%\input_1A:/app/input_1A" -v "%cd%\output_1A:/app/output_1A" adobe-hackathon:prod
) else (
    echo ❌ Build failed!
    exit /b 1
)
goto :end

:build_both
echo Building both development and production images...
call :build_dev
call :build_prod
goto :end

:build_compose
echo Building with docker-compose...
docker-compose build %CACHE_OPTION%
if %ERRORLEVEL% EQU 0 (
    echo ✅ All services built with docker-compose!
    echo ⚠️  Run with: docker-compose up [service-name]
) else (
    echo ❌ Compose build failed!
    exit /b 1
)
goto :end

:clean
echo Cleaning up Docker images and cache...
docker system prune -f
docker image prune -f
echo ✅ Docker cleanup completed!
goto :end

:usage
echo ❌ Unknown build type: %BUILD_TYPE%
echo.
echo Usage: %0 [dev^|prod^|both^|compose^|clean] [--no-cache^|--cache]
echo.
echo Build types:
echo   dev        - Fast development build (minimal dependencies)
echo   prod       - Full production build (all features)
echo   both       - Build both dev and prod images
echo   compose    - Build using docker-compose
echo   clean      - Clean up Docker cache and unused images
echo.
echo Cache options:
echo   --no-cache - Force rebuild (default)
echo   --cache    - Use cached layers
exit /b 1

:end
echo.
echo 🎉 Build completed successfully!
echo.
echo Available commands:
echo   🔍 Test validation:    docker run --rm -v "%cd%\output_1A:/app/output_1A" adobe-hackathon:dev
echo   🚀 Run full pipeline:  docker run --rm -v "%cd%\input_1A:/app/input_1A" -v "%cd%\output_1A:/app/output_1A" adobe-hackathon:prod
echo   📊 Run with compose:   docker-compose up validation
