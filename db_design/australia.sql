\c personal_stock; 
CREATE SCHEMA australia;

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



CREATE TYPE personal_stock.australia.stock_exchange AS ENUM (
    'AU'
);

ALTER TYPE personal_stock.australia.stock_exchange OWNER TO :username;

SET default_tablespace = '';

-- Default: End of day data
CREATE TABLE personal_stock.australia.transaction (
    stock_exchange personal_stock.australia.stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open double precision,
    high double precision,
    low double precision,
    close double precision,
    adjusted_close double precision,
    volume bigint
);


ALTER TABLE personal_stock.australia.transaction OWNER TO :username;

ALTER TABLE ONLY personal_stock.australia.transaction
    ADD CONSTRAINT transaction_unique_key UNIQUE (stock_exchange, stock_code, date);

SET default_table_access_method = heap;

CREATE TABLE personal_stock.australia.stock_info (
    company_name character varying,
    stock_code character varying NOT NULL,
    stock_exchange personal_stock.australia.stock_exchange NOT NULL,
    last_updated_date DATE NOT NULL,
    fundamental json
);

ALTER TABLE personal_stock.australia.stock_info OWNER TO :username;

ALTER TABLE ONLY personal_stock.australia.stock_info
    ADD CONSTRAINT stock_info_pkey PRIMARY KEY (stock_code);

ALTER TABLE personal_stock.australia.transaction
    ADD CONSTRAINT stock_code_f_key FOREIGN KEY (stock_code) REFERENCES personal_stock.australia.stock_info(stock_code) DEFERRABLE;