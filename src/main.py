import os
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime as datetime_type
from typing import Annotated
import math


# data format in database
class Ticker_data(SQLModel, table=True):
    # datetime field for the record's timestamp
    datetime: datetime_type = Field(primary_key=True)
    # opening price of the day
    open: float
    # highest price of the day
    high: float
    # lowest price of the day
    low: float
    # closing price of the day
    close: float
    # traded volume
    volume: int
    # name of the instrument
    instrument: str


# response model for strategy performance
class StrategyPerformance(SQLModel):
    # total return from the strategy
    total_return: float
    # number of trades executed
    number_of_trades: int
    # number of buy signals generated
    buy_signals: int
    # number of sell signals generated
    sell_signals: int


# get env variables
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# check for missing parameters
if DB_NAME == None or DB_USERNAME == None or DB_PASSWORD == None:
    print("Missing database parameters")
    exit()

# default parameters
if DB_HOST == None:
    DB_HOST = "localhost"

if DB_PORT == None:
    DB_PORT = "5432"

# construct database url
database_url = "postgresql://{username}:{password}@{host}:{port}/{dbname}".format(
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
)

# create database engine
engine = create_engine(database_url)


# get session
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# create FastApi app
app = FastAPI()


# get all data in the database
@app.get("/data")
def read_data(session: SessionDep) -> list[Ticker_data]:
    datas = session.exec(select(Ticker_data)).all()
    return datas


# post a data to database
@app.post("/data")
def create_data(data: Ticker_data, session: SessionDep) -> Ticker_data:
    session.add(data)
    session.commit()
    session.refresh(data)
    return data


# fetch data and calculate strategy performance
@app.get("/strategy/performance", response_model=StrategyPerformance)
def calculate_performance(session: SessionDep) -> StrategyPerformance:
    # fetch data from the database
    query = select(Ticker_data.datetime, Ticker_data.close).order_by(
        Ticker_data.datetime
    )
    datas = session.exec(query).all()

    # windows for calculating moving averages
    short_window = 20
    long_window = 100

    # validate if data is sufficient
    if len(datas) < long_window:
        raise HTTPException(
            status_code=400, detail="Insufficient data for performance calculation"
        )

    # convert data to pandas DataFrame
    data_dicts = [{"datetime": data.datetime, "close": data.close} for data in datas]
    df = pd.DataFrame(data_dicts)

    # calculate mean
    df["short_ma"] = df["close"].rolling(window=short_window).mean()
    df["long_ma"] = df["close"].rolling(window=long_window).mean()

    # generate buy/sell signals
    df["signal"] = 0
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1  # buy signal
    df.loc[df["short_ma"] <= df["long_ma"], "signal"] = -1  # sell signal

    # calculate performance
    df["position"] = df["signal"].shift(1)  # lag signal to simulate trades
    df["daily_return"] = df["close"].pct_change()
    df["strategy_return"] = df["daily_return"] * df["position"]

    # performance metrics
    total_return = df["strategy_return"].sum()
    buy_signals = (df["signal"] == 1).sum()
    sell_signals = (df["signal"] == -1).sum()
    number_of_trades = buy_signals + sell_signals

    return StrategyPerformance(
        total_return=total_return,
        number_of_trades=number_of_trades,
        buy_signals=buy_signals,
        sell_signals=sell_signals,
    )
