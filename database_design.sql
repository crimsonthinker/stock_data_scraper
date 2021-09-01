--
-- PostgreSQL database dump
--

-- Dumped from database version 12.7 (Ubuntu 12.7-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.7 (Ubuntu 12.7-0ubuntu0.20.04.1)

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

--
-- Name: vietnam_stock_exchange; Type: TYPE; Schema: public; Owner: khoa
--

CREATE TYPE public.vietnam_stock_exchange AS ENUM (
    'HSX',
    'HNX',
    'UPCOM'
);


ALTER TYPE public.vietnam_stock_exchange OWNER TO khoa;

--
-- Name: TYPE vietnam_stock_exchange; Type: COMMENT; Schema: public; Owner: khoa
--

COMMENT ON TYPE public.vietnam_stock_exchange IS 'enumeration for stock exchanges';


--
-- Name: vietnam_stock_index; Type: TYPE; Schema: public; Owner: khoa
--

CREATE TYPE public.vietnam_stock_index AS ENUM (
    'VNINDEX',
    'HNX-INDEX'
);


ALTER TYPE public.vietnam_stock_index OWNER TO khoa;

SET default_tablespace = '';

--
-- Name: transaction; Type: TABLE; Schema: public; Owner: khoa
--

CREATE TABLE public.transaction (
    stock_exchange public.vietnam_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
)
PARTITION BY LIST (stock_exchange);


ALTER TABLE public.transaction OWNER TO khoa;

SET default_table_access_method = heap;

--
-- Name: hnx_transaction; Type: TABLE; Schema: public; Owner: khoa
--

CREATE TABLE public.hnx_transaction (
    stock_exchange public.vietnam_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);
ALTER TABLE ONLY public.transaction ATTACH PARTITION public.hnx_transaction FOR VALUES IN ('HNX');


ALTER TABLE public.hnx_transaction OWNER TO khoa;

--
-- Name: hsx_transaction; Type: TABLE; Schema: public; Owner: khoa
--

CREATE TABLE public.hsx_transaction (
    stock_exchange public.vietnam_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);
ALTER TABLE ONLY public.transaction ATTACH PARTITION public.hsx_transaction FOR VALUES IN ('HSX');


ALTER TABLE public.hsx_transaction OWNER TO khoa;

--
-- Name: stock_index; Type: TABLE; Schema: public; Owner: khoa
--

CREATE TABLE public.stock_index (
    stock_index public.vietnam_stock_index NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);


ALTER TABLE public.stock_index OWNER TO khoa;

--
-- Name: stock_info; Type: TABLE; Schema: public; Owner: khoa
--

CREATE TABLE public.stock_info (
    company_name character varying,
    free_float bigint NOT NULL,
    first_transaction_date date NOT NULL,
    stock_code character varying NOT NULL,
    listing_volume bigint NOT NULL,
    stock_exchange public.vietnam_stock_exchange NOT NULL
);


ALTER TABLE public.stock_info OWNER TO khoa;

--
-- Name: upcom_transaction; Type: TABLE; Schema: public; Owner: khoa
--

CREATE TABLE public.upcom_transaction (
    stock_exchange public.vietnam_stock_exchange NOT NULL,
    stock_code character varying(20) NOT NULL,
    date date NOT NULL,
    open_price double precision,
    highest_price double precision,
    lowest_price double precision,
    close_price double precision,
    volume bigint
);
ALTER TABLE ONLY public.transaction ATTACH PARTITION public.upcom_transaction FOR VALUES IN ('UPCOM');


ALTER TABLE public.upcom_transaction OWNER TO khoa;

--
-- Name: transaction transaction_unique_key; Type: CONSTRAINT; Schema: public; Owner: khoa
--

ALTER TABLE ONLY public.transaction
    ADD CONSTRAINT transaction_unique_key UNIQUE (stock_exchange, stock_code, date);


--
-- Name: hnx_transaction hnx_transaction_stock_exchange_stock_code_date_key; Type: CONSTRAINT; Schema: public; Owner: khoa
--

ALTER TABLE ONLY public.hnx_transaction
    ADD CONSTRAINT hnx_transaction_stock_exchange_stock_code_date_key UNIQUE (stock_exchange, stock_code, date);


--
-- Name: hsx_transaction hsx_transaction_stock_exchange_stock_code_date_key; Type: CONSTRAINT; Schema: public; Owner: khoa
--

ALTER TABLE ONLY public.hsx_transaction
    ADD CONSTRAINT hsx_transaction_stock_exchange_stock_code_date_key UNIQUE (stock_exchange, stock_code, date);


--
-- Name: stock_index stock_index_unique_key; Type: CONSTRAINT; Schema: public; Owner: khoa
--

ALTER TABLE ONLY public.stock_index
    ADD CONSTRAINT stock_index_unique_key UNIQUE (stock_index, date);


--
-- Name: stock_info stock_info_pkey; Type: CONSTRAINT; Schema: public; Owner: khoa
--

ALTER TABLE ONLY public.stock_info
    ADD CONSTRAINT stock_info_pkey PRIMARY KEY (stock_code);


--
-- Name: upcom_transaction upcom_transaction_stock_exchange_stock_code_date_key; Type: CONSTRAINT; Schema: public; Owner: khoa
--

ALTER TABLE ONLY public.upcom_transaction
    ADD CONSTRAINT upcom_transaction_stock_exchange_stock_code_date_key UNIQUE (stock_exchange, stock_code, date);


--
-- Name: hnx_transaction_stock_exchange_stock_code_date_key; Type: INDEX ATTACH; Schema: public; Owner: khoa
--

ALTER INDEX public.transaction_unique_key ATTACH PARTITION public.hnx_transaction_stock_exchange_stock_code_date_key;


--
-- Name: hsx_transaction_stock_exchange_stock_code_date_key; Type: INDEX ATTACH; Schema: public; Owner: khoa
--

ALTER INDEX public.transaction_unique_key ATTACH PARTITION public.hsx_transaction_stock_exchange_stock_code_date_key;


--
-- Name: upcom_transaction_stock_exchange_stock_code_date_key; Type: INDEX ATTACH; Schema: public; Owner: khoa
--

ALTER INDEX public.transaction_unique_key ATTACH PARTITION public.upcom_transaction_stock_exchange_stock_code_date_key;


--
-- Name: transaction stock_code_f_key; Type: FK CONSTRAINT; Schema: public; Owner: khoa
--

ALTER TABLE public.transaction
    ADD CONSTRAINT stock_code_f_key FOREIGN KEY (stock_code) REFERENCES public.stock_info(stock_code) DEFERRABLE;


--
-- Name: CONSTRAINT stock_code_f_key ON transaction; Type: COMMENT; Schema: public; Owner: khoa
--

COMMENT ON CONSTRAINT stock_code_f_key ON public.transaction IS 'foreign key for stock code';


--
-- PostgreSQL database dump complete
--

