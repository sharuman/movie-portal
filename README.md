# ase-movie-catalogue

## Setup
- Python 3.9.6
- Postgres
### Conda environment
1. `conda env create -f environment.yml`
2. `conda activate ase_movies`

To update the environment use `conda env update -f environment.yml --prune`.



## Dockerized Setup
1. Install docker
2. Go to the rootfolder of the project and run 'docker compose up'
  a) Alternatively, just execute the startDockerized.bat file in the root folder

This will create and start 3 different services, one for postgres, one for django (Which will run django's migrate and runserver commands) and one for pgadmin. 
Afterwards, django and pgadmin can be accessed via localhost:SERVICEPORT, where SERVICEPORT is defined in the docker-compose file.
Pg admin login and server info can also be found in the docker-compose file. The services can use the hostname of postgres (Defined in docker-compose file) instead of an actual IP. (E.g. "postgres" for the settings.py and the pgadmin server hostname when adding one)

Services can be rebuild and restarted via docker commands.
Examples for that:

Rebuilding and restarting django: (rebuildDjangoService.bat contains those lines)
1. docker-compose stop django
2. docker compose build django
3. docker compose restart django

Rebuilding and restarting postgres: (rebuildPostgresService.bat contains those lines)
docker-compose stop postgres
docker compose build postgres
docker compose restart postgres
