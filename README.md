# Movie Portal

## Setup
- Python 3.9.6
- Postgres
- Run `createuser -s postgres`
- Create `movie_portal` database

### Conda environment
1. `conda env create -f environment.yml`
2. `conda activate ase_movies`

To update the environment use `conda env update -f environment.yml --prune`.

### Migrations
1. `cd moviePortalSite`
2. `python manage.py makemigrations`
3. `python manage.py migrate`