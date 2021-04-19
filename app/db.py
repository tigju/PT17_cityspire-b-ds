"""Database functions"""

import os
from fastapi import APIRouter, Depends
import sqlalchemy
from dotenv import load_dotenv
import databases
import asyncio
from typing import Union, Iterable
from pypika import Query, Table, CustomFunction
from pypika.terms import Field

Field_ = Union[Field, str]

load_dotenv()
database_url = os.getenv("DATABASE_URL")
database = databases.Database(database_url)

router = APIRouter()


@router.get("/info")
async def get_url():
    """Verify we can connect to the database,
    and return the database URL in this format:

    dialect://user:password@host/dbname

    The password will be hidden with ***
    """

    url_without_password = repr(database.url)
    return {"database_url": url_without_password}


@router.get("/all_cities")
async def get_cities():
    """
    Get available cities from DB
    """
    data = Table("data")
    
    columns = (
        data["City"].as_("City"),
        data["State"].as_("State"),
    )

    q = (
        Query.from_(data)
        .select(*columns)
    )
    value = await database.fetch_all(str(q))
    return value


async def select(columns: Union[Iterable[Field_], Field_], city):
    data = Table("data")
    if type(columns) == str or type(columns) == Field:
        q = Query.from_(data).select(columns)
    else:
        cols = [data[x] for x in columns]
        q = Query.from_(data).select(*cols)

    q = q.where(data.City == city.city).where(data.State == city.state)

    value = await database.fetch_one(str(q))
    return value


async def select_all(city):
    """Fetch all data at once

    Fetch data from DB

    args:
        city: selected city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """
    data = Table("data")
    di_fn = CustomFunction("ROUND", ["number"])
    columns = (
        # 'lat', 'lon'
        data["lat"].as_("latitude"),
        data["lon"].as_("longitude"),
        data["Crime Rating"].as_("crime"),
        data["Rent"].as_("rental_price"),
        data["Air Quality Index"].as_("air_quality_index"),
        data["Population"].as_("population"),
        data["Nearest"].as_("nearest_string"),
        data["Good Days"].as_("good_days"),
        data["Crime Rate per 1000"].as_("crime_rate_ppt"),
        di_fn(data["Diversity Index"] * 100).as_("diversity_index"),
    )

    q = (
        Query.from_(data)
        .select(*columns)
        .where(data.City == city.city)
        .where(data.State == city.state)
    )
    value = await database.fetch_one(str(q))
    return value

  
async def select_housing_price_averages(city):
    """Fetch housing price averages per city
    
    The averages includes single family homes, condos, one bedroom,
    two bedroom, three bedroom, four bedroom, and five and up bedroom averages.
    
    Fetch data from DB
    
    args:
        city: selected city
        
    returns:
        Dictionary that contains the requested data, which is converted by fastAPI to a json object.
    """
    prices = Table("data")
    
    columns = (
        prices['SingleFamilyHousingAvgValue'].as_("single_family_housing_avg_price"),
        prices['CondoAvgValue'].as_("condo_avg_price"),
        prices['1-BedroomAvgValue'].as_("1_bedroom_avg_price"),
        prices['2-BedroomAvgValue'].as_("2_bedroom_avg_price"),
        prices['3-BedroomAvgValue'].as_("3_bedroom_avg_price"),
        prices['4-BedroomAvgValue'].as_("4_bedroom_avg_price"),
        prices['5+-BedroomAvgValue'].as_("5_and_up_bedroom_avg_price"),
    )
    
    q = (
        Query.from_(prices)
        .select(*columns)
        .where(prices.City == city.city)
        .where(prices.State == city.state)
    )
    value = await database.fetch_one(str(q))
    return value


async def select_weather_daily(city):
    """Fetch weather forecast per city

    Fetch data from DB

    args:
        city: selected city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """
    forecast = Table("weather_daily_forecast")

    columns = (
        forecast["date"].as_("date"),
        forecast["temperature_pred"].as_("average_temperature"),
        forecast["temp_lower_pred"].as_("min_temperature"),
        forecast["temp_upper_pred"].as_("max_temperature"),
    )

    q = (
        Query.from_(forecast)
        .select(*columns)
        .where(forecast.city == city.city)
        .where(forecast.state == city.state)
    )
    value = await database.fetch_all(str(q))
    return value

  
async def select_weather_monthly(city):
    """Fetch weather forecast per city

    Fetch data from DB

    args:
        city: selected city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """
    forecast = Table("weather_monthly_forecast")

    columns = (
        forecast["date"].as_("date"),
        forecast["temperature_pred"].as_("average_temperature"),
        forecast["temp_lower_pred"].as_("min_temperature"),
        forecast["temp_upper_pred"].as_("max_temperature"),
    )

    q = (
        Query.from_(forecast)
        .select(*columns)
        .where(forecast.city == city.city)
        .where(forecast.state == city.state)
    )
    value = await database.fetch_all(str(q))
    return value
    
#############
# Begin My Code (Andrew Rust)
# Below was an attempt to access the postgresql db.
# Error in my code making the csv file.  I'll have to redo it.

# async def select_available_jobs(city):
#     """Fetch random jobs per city
    
#     Fetch data from DB
    
#     args:
#         city: selected city
        
#     returns:
#         Dictionary that contains the requested data, which is converted by fastAPI to a json object.
#     """
#     jobs = Table('random_jobs')
    
#     columns = (
#         jobs['Job'].as_('random_avail_jobs')
#     )
    
#     q = (
#         Query.from_(jobs)
#         .select(*columns)
#         .where(jobs.City == city.city)
#     )
#     value = await database.fetch_one(str(q))
#     return value

# End code (Andrew Rust)
#############