#!/bin/bash
set -e

#drop the existing ticker_data table if it exists
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  DROP TABLE IF EXISTS ticker_data;
EOSQL

#create the ticker_data table
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /create_ticker_table.sql
