-- copy data from the csv file into the ticker_data table
\copy ticker_data(datetime, close, high, low, open, volume, instrument) FROM '/HINDALCO.csv' DELIMITER ',' CSV HEADER;
