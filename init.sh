#!/bin/bash

docker run -v /home/khoa/repo/vn_stock_data_scraper/db_design:/home/db_design --name personal-postgres -e POSTGRES_USER=khoa -e POSTGRES_PASSWORD=khoa -d postgres;

# Initiate Autralia stock
docker exec -it personal-postgres psql -U khoa -f /home/db_design/australia.sql

# TODO: Initiate Vietnam stock