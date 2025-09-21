@echo off
echo ================================
echo   GenAI Legal - Deployment Script
echo ================================

echo.
echo Select deployment option:
echo 1. Deploy Django Backend only
echo 2. Deploy FastAPI Service only  
echo 3. Deploy both Backend services
echo 4. Show deployment status
echo 5. Exit

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto deploy_django
if "%choice%"=="2" goto deploy_fastapi
if "%choice%"=="3" goto deploy_both
if "%choice%"=="4" goto show_status
if "%choice%"=="5" goto exit

:deploy_django
echo.
echo Deploying Django Backend...
cd Final_Backend
gcloud app deploy app.yaml --quiet
echo Django Backend deployed successfully!
goto end

:deploy_fastapi
echo.
echo Deploying FastAPI Service...
cd Final_Backend\geniai
gcloud app deploy fastapi.yaml --quiet
echo FastAPI Service deployed successfully!
goto end

:deploy_both
echo.
echo Deploying Django Backend...
cd Final_Backend
gcloud app deploy app.yaml --quiet
echo Django Backend deployed!

echo.
echo Deploying FastAPI Service...
cd geniai
gcloud app deploy fastapi.yaml --quiet
echo FastAPI Service deployed!
echo.
echo Both services deployed successfully!
goto end

:show_status
echo.
echo Current deployment status:
echo.
echo Django Backend: https://gen-ai-legal.uc.r.appspot.com
echo FastAPI Service: https://fastapi-dot-gen-ai-legal.uc.r.appspot.com
echo Frontend: https://genai-silk-beta.vercel.app
echo.
echo Checking service health...
curl -s https://gen-ai-legal.uc.r.appspot.com/api/ > nul && echo Django Backend: ONLINE || echo Django Backend: OFFLINE
curl -s https://fastapi-dot-gen-ai-legal.uc.r.appspot.com/api/health > nul && echo FastAPI Service: ONLINE || echo FastAPI Service: OFFLINE
goto end

:exit
echo Goodbye!
goto end

:end
echo.
pause