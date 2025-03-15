\c personal_stock; 
CREATE SCHEMA world;

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

\set username 'khoa';

-- There're more indexes, but just covered thw two main one
CREATE TYPE personal_stock.world.stock_index AS ENUM (
    'S&P 500',
    'S&P/ASX 200',
    'Nikkei 225',
    'Hang Seng',
    'FTSE 100',
    'Dow Jones',
    'NASDAQ',
    'Vietnam Index'
);

ALTER TYPE personal_stock.world.stock_index OWNER TO :username;

CREATE TYPE personal_stock.world.countries AS ENUM (
    'vietnam',
    'united_states',
    'australia',
    'japan',
    'hong_kong',
    'united_kingdom'
);

ALTER TYPE personal_stock.world.countries OWNER TO :username;



CREATE TABLE personal_stock.world.stock_indexes (
    stock_index personal_stock.world.stock_index NOT NULL,
    country personal_stock.world.countries NOT NULL,
    date date NOT NULL,
    open double precision,
    high double precision,
    low double precision,
    close double precision,
    volume bigint,
    dividends double precision,
    stock_splits double precision
);

ALTER TABLE personal_stock.world.stock_indexes OWNER TO :username;

ALTER TABLE ONLY personal_stock.world.stock_indexes
    ADD CONSTRAINT stock_index_unique_key UNIQUE (stock_index, date);


CREATE TABLE personal_stock.world.daily_average_exchange_rate_usd_based (
    date date NOT NULL,
    vnd double precision,
    aud double precision,
    jpy double precision,
    hkd double precision,
    gbp double precision
);

ALTER TABLE personal_stock.world.daily_average_exchange_rate_usd_based OWNER TO :username;

ALTER TABLE ONLY personal_stock.world.daily_average_exchange_rate_usd_based
    ADD CONSTRAINT daily_average_exchange_rate_usd_based_unique_key UNIQUE (date);