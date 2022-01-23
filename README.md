# ASE Movie Catalogue Project
## Dockerized Setup
1. Install Docker
2. `cp .env.example .env`
3. Set the variables in `.env` file accordingly
4. Go to the root folder of the project and run `docker compose up`. Alternatively, just execute the `startDockerized.bat` file in the root folder (only valid for Windows OS). This will create and start 3 different services, one for postgres, one for django (which will run django's migrate and runserver commands) and one for pgdmin.

### Connections
Complete connection values can be found in the `docker-compose.yml` file.
- To connect to the web application use `localhost:8000`
- pgAdmin can be accessed on `localhost:5051`
- In case you wish to use an external GUI to connect to the database, you can use `127.0.0.1` as hostname and `5432` as port.

**NOTE**: values set in `docker-compose.yml` should reflect the values in `settings.py` file (and viceversa).
### Docker services rebuild and restart

Rebuilding and restarting `django` (alternatively, you can run `rebuildDjangoService.bat` which will run the aforementioned commands):
1. `docker compose stop django`
2. `docker compose build django`
3. `docker compose restart django`

Rebuilding and restarting `postgres` (alternatively, you can run `rebuildPostgresService.bat` which will run the following commands):
1. `docker compose stop postgres`
2. `docker compose build postgres`
3. `docker compose restart postgres`

## Run
Once the docker containers are running you must follow the steps below in case you do not have the database dump:
1. `docker exec django-container python manage.py migrate`
2. `docker exec -it django-container python manage.py createsuperuser`
3. Backoffice:
    - url: http://localhost:8000/admin/
    - credentials: use the username and password set in the previous step
4. `docker exec django-container python manage.py import_movies`


### Django Help
#### Get rid of app related tables and start over again:
1. `docker exec django-container python manage.py migrate your_app zero` will drop all the tables related to _your_app_ from the database
2. remove the migration(s) in the `migrations` directory
3. `docker exec django-container python manage.py makemigrations your_app` generate the migrations
4. `docker exec django-container python manage.py migrate your_app` apply the migrations to the database

#### Removing all model data: (But keeping the user table)
`docker exec django-container python manage.py flush_movies`

#### Removing data from ALL tables (Including user table!) 
`docker exec django-container bash -c "echo yes| python manage.py flush"` -> first pipe yes into command (for confirmation of the command), then flush database

