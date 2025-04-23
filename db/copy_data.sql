-- copy data from the csv file into the ticker_data table
\copy ticker_data(datetime, close, high, low, open, volume, instrument) FROM '/home/pushkar/DevDen/InvstoAssignment/HINDALCO.csv' DELIMITER ',' CSV HEADER;
