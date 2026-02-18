@echo off
echo =======================================================
echo 🧹 Cleaning up Docker environment...
echo 🛑 Stopping and removing old containers...
docker-compose down

echo 🗑️  Removing dangling images to save disk space...
docker image prune -f

echo.
echo 🏗️  Building images and starting new containers...
docker-compose up --build -d

echo.
echo 👀 Showing logs (Streamlit and FastAPI)...
echo (Press Ctrl+C to exit logs, the apps will keep running)
echo =======================================================
docker-compose logs -f