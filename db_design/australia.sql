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

ALTER TYPE public.australia_stock_exchange OWNER TO :username;

COMMENT ON TYPE public.australia_stock_exchange IS 'enumeration for stock exchanges';

-- There're more indexes, but just covered thw two main one
CREATE TYPE public.australia_stock_index AS ENUM (
    'ASX200',
    'ASX200Finance'
);

ALTER TYPE public.australia_stock_index OWNER TO :username;

SET default_tablespace = '';

CREATE TABLE public.australia_transaction (
    stock_exchange public.australia_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
)
PARTITION BY LIST (stock_exchange);


ALTER TABLE public.australia_transaction OWNER TO :username;

SET default_table_access_method = heap;

CREATE TABLE public.asx_transaction (
    stock_exchange public.australia_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);


ALTER TABLE public.asx_transaction OWNER TO :username;

CREATE TABLE public.nsx_transaction (
    stock_exchange public.australia_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);

ALTER TABLE public.nsx_transaction OWNER TO :username;

CREATE TABLE public.apx_transaction (
    stock_exchange public.australia_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);

ALTER TABLE public.apx_transaction OWNER TO :username;


CREATE TABLE public.australia_stock_indexes (
    stock_index public.australia_stock_index NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);


ALTER TABLE public.australia_stock_indexes OWNER TO :username;

CREATE TABLE public.australia_stock_info (
    company_name character varying,
    free_float bigint NOT NULL,
    first_transaction_date date NOT NULL,
    stock_code character varying NOT NULL,
    listing_volume bigint NOT NULL,
    stock_exchange public.australia_stock_exchange NOT NULL
);


ALTER TABLE public.australia_stock_info OWNER TO :username;

ALTER TABLE ONLY public.australia_transaction ATTACH PARTITION public.asx_transaction FOR VALUES IN ('ASX');

ALTER TABLE ONLY public.australia_transaction ATTACH PARTITION public.nsx_transaction FOR VALUES IN ('NSX');

ALTER TABLE ONLY public.australia_transaction ATTACH PARTITION public.apx_transaction FOR VALUES IN ('APX');

ALTER TABLE ONLY public.australia_transaction
    ADD CONSTRAINT australia_transaction_unique_key UNIQUE (stock_exchange, stock_code, date);

ALTER TABLE ONLY public.asx_transaction
    ADD CONSTRAINT asx_transaction_stock_exchange_stock_code_date_key UNIQUE (stock_exchange, stock_code, date);

ALTER TABLE ONLY public.nsx_transaction
    ADD CONSTRAINT nsx_transaction_stock_exchange_stock_code_date_key UNIQUE (stock_exchange, stock_code, date);

ALTER TABLE ONLY public.apx_transaction
    ADD CONSTRAINT apx_transaction_stock_exchange_stock_code_date_key UNIQUE (stock_exchange, stock_code, date);

ALTER TABLE ONLY public.australia_stock_indexes
    ADD CONSTRAINT stock_index_unique_key UNIQUE (stock_index, date);

ALTER TABLE ONLY public.australia_stock_info
    ADD CONSTRAINT stock_info_pkey PRIMARY KEY (stock_code);


ALTER INDEX public.australia_transaction_unique_key ATTACH PARTITION public.asx_transaction_stock_exchange_stock_code_date_key;

ALTER INDEX public.australia_transaction_unique_key ATTACH PARTITION public.nsx_transaction_stock_exchange_stock_code_date_key;

ALTER INDEX public.australia_transaction_unique_key ATTACH PARTITION public.apx_transaction_stock_exchange_stock_code_date_key;

ALTER TABLE public.australia_transaction
    ADD CONSTRAINT stock_code_f_key FOREIGN KEY (stock_code) REFERENCES public.australia_stock_info(stock_code) DEFERRABLE;

COMMENT ON CONSTRAINT stock_code_f_key ON public.australia_transaction IS 'foreign key for stock code';