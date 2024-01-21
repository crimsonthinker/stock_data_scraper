#!/bin/bash

# FIXME: Setup conda environment

docker run -v /home/khoa/repo/stock_data_scraper/db_design:/home/db_design --name personal-postgres -p 5432:5432 -e POSTGRES_USER=khoa -e POSTGRES_PASSWORD=khoa -d postgres;

docker exec -it personal-postgres psql -U khoa -c "CREATE DATABASE personal_stock";

# Initiate Autralia stock
docker exec -it personal-postgres psql -U khoa -f /home/db_design/australia.sql;

# TODO: Initiate Vietnam stock
docker exec -it personal-postgres psql -U khoa -f /home/db_design/vietnam.sql;

docker exec -it personal-postgres psql -U khoa -f /home/db_design/world.sql;