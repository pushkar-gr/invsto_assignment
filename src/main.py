import os
from fastapi import Depends, FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime as datetime_type
from typing import Annotated


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
