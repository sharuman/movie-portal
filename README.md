# ASE Movie Catalogue Project
## Dockerized Setup
1. Install Docker
2. Go to the root folder of the project and run `docker compose up`. Alternatively, just execute the `startDockerized.bat` file in the root folder (only valid for Windows OS). This will create and start 3 different services, one for postgres, one for django (which will run django's migrate and runserver commands) and one for pgdmin.

### Connections
Complete connection values can be found in the `docker-compose.yml` file.
- To connect to the web application use `localhost:8000`
- pgAdmin can be accessed on `localhost:5051`
- In case you wish to use an external GUI to connect to the database, you can use `127.0.0.1` as hostname and `5432` as port.

**NOTE**: values set in `docker-compose.yml` should reflect the values in `settings.py` file (and viceversa).
### Docker services rebuild and restart

Rebuilding and restarting `django` (alternatively, you can run `rebuildDjangoService.bat` which will run the aforementioned commands):
1. `docker-compose stop django`
2. `docker compose build django`
3. `docker compose restart django`

Rebuilding and restarting `postgres` (alternatively, you can run `rebuildPostgresService.bat` which will run the following commands):
1. `docker-compose stop postgres`
2. `docker compose build postgres`
3. `docker compose restart postgres`
