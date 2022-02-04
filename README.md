# ASE Movie Catalogue Project
## Dockerized Setup
1. Install Docker
2. `cp .env.example .env`
3. Set the variables in `.env` file accordingly
4. Go to the root folder of the project and run `docker compose up`. Alternatively, just execute the `startDockerized.bat` file in the root folder (only valid for Windows OS). This will create and start 3 different services, one for postgres, one for django (which will run django's migrate and runserver commands) and one for pgdmin.
5. Import database if provided (see next section for database connection)
6. Extract `posters.zip` and put the poster images in `static/images/posters`
7. Backoffice:
    - url: http://localhost:8000/admin/
    - username: admin
    - password: admin

### Connections
Complete connection values can be found in the `docker-compose.yml` file.
- To connect to the web application use `localhost:8000`
- pgAdmin can be accessed on `localhost:5051`
- In case you wish to use an external GUI to connect to the database, you can use `127.0.0.1` as hostname and `5432` as port.

**NOTE**: values set in `docker-compose.yml` should reflect the values in `settings.py` file (and viceversa).
### Docker services rebuild and restart

Rebuilding and restarting `django` (alternatively, you can run `rebuildDjangoService.bat` which will run the aforementioned commands):
1. `docker compose stop django`
2. `docker compose build --no-cache --pull django`
3. `docker compose restart django`

Rebuilding and restarting `postgres` (alternatively, you can run `rebuildPostgresService.bat` which will run the following commands):
1. `docker compose stop postgres`
2. `docker compose build --no-cache postgres`
3. `docker compose restart postgres`

## Manual Setup
Once the docker containers are running you must follow the steps below in case you do not have the database dump and movie posters:
1. Download [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset)
2. `docker exec django-container python manage.py migrate`
3. `docker exec -it django-container python manage.py createsuperuser`
4. Backoffice:
    - url: http://localhost:8000/admin/
    - credentials: use the username and password set in the previous step
5. create `import` folder in the root directory and place the `.csv` files of _step 0_ in it
6. update the paths in the `.env` file accordingly
7. `docker exec django-container python manage.py import_movies`. Pass `--flush` option to empty movies app db tables (except user table).
	The import_movies function imports by default only a max of 1000 rows per csv. To change the number of imported rows, pass the option -max_rows X where X is your desired maximum number of rows
8. Create [The Movie Database API](https://developers.themoviedb.org/3/getting-started/introduction). This api key is needed to show movies' posters. Update the `.env` file accordingly.
9. `docker exec django-container python manage.py get_movie_posters`. The posters will be saved in `static/images/posters` directory.


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
