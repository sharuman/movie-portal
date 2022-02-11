docker-compose stop postgres
docker compose build --no-cache postgres
docker compose restart postgres
pause