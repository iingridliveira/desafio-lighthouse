\set ON_ERROR_STOP on
SET search_path TO lh_nautical, public;

-- Os arquivos são montados em /data pelo docker-compose.
-- A carga não transforma nem corrige os dados: o objetivo é permitir a EDA bruta.
\copy brands FROM '/data/brands.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');
\copy categories FROM '/data/categories.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');
\copy customers FROM '/data/customers.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');
\copy employees FROM '/data/employees.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');
\copy orders FROM '/data/orders.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');
\copy fiscal_invoices FROM '/data/fiscal_invoices.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

ANALYZE;
