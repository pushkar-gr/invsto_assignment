--create the ticker_data table
CREATE TABLE ticker_data (
  datetime TIMESTAMP NOT NULL,
  open DECIMAL NOT NULL,
  high DECIMAL NOT NULL,
  low DECIMAL NOT NULL,
  close DECIMAL NOT NULL,
  volume INTEGER NOT NULL,
  instrument VARCHAR(50) NOT NULL
);

