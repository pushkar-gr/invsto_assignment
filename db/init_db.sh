#!/bin/bash
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /create_ticker_table.sql
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /copy_data.sql
