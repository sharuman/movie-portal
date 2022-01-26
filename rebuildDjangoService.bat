docker-compose stop django
docker compose build --no-cache --pull django
docker compose restart django
pause
