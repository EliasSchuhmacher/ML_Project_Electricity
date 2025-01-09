import os
from datetime import datetime, timedelta
import time
import requests
import pandas as pd
import json
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import openmeteo_requests
import requests_cache
from retry_requests import retry
from pathlib import Path
import pytz


def make_get_request(url:str):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        print("Request failed. Status:", response.status_code)
        raise requests.exceptions.RequestException(response.status_code)

    return data

def get_tomorrows_electricity_prices(price_area: str):
    # Set the timezone to Swedish time
    swedish_tz = pytz.timezone('Europe/Stockholm')
    now = datetime.now(swedish_tz)

    # if it's after 12:15, get the prices for tomorrow, otherwise get the prices for today
    # if now.hour >= 12 and now.minute >= 15:
        # Get tomorrow's date
    tomorrow = now + timedelta(days=1)
    year = tomorrow.strftime('%Y')
    month = tomorrow.strftime('%m')
    day = tomorrow.strftime('%d')
    # else:
    #     # Get today's date
    #     today = now
    #     year = today.strftime('%Y')
    #     month = today.strftime('%m')
    #     day = today.strftime('%d')

    print("Fetching electricity prices...")
    print(f"Date: {year}-{month}-{day}")
    print(f"Price area: {price_area}")

    # Format the URL
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{month}-{day}_{price_area}.json"

    # Make the GET request
    try:
        data = make_get_request(url)

        # Parse the data into a DataFrame
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time_start'], utc=True)
        df['pricearea'] = price_area
        # Convert the price to EUR/MWh
        df['spotpriceeur'] = df['EUR_per_kWh'] * 1000
        
        # Select and reorder the columns
        df = df[['time', 'pricearea', 'spotpriceeur']]
        return df
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data: {e}")
        return None
    
def get_hourly_weather_forecast(latitude, longitude):

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "cloud_cover", "wind_speed_10m"],
        "daily": "sunshine_duration",
        "timezone": "Europe/Berlin"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    # print(hourly_dataframe)

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_sunshine_duration = daily.Variables(0).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["sunshine_duration"] = daily_sunshine_duration

    daily_dataframe = pd.DataFrame(data = daily_data)
    # print(daily_dataframe)

    # rename the date column of the hourly dataframe to time
    hourly_dataframe.rename(columns = {"date": "time"}, inplace = True)

    # Merge the sunshine duration into the hourly dataframe
    # Extract the date from the hourly dataframe
    hourly_dataframe['date'] = hourly_dataframe['time'].dt.date

    # Convert the date column in daily_dataframe to date object
    daily_dataframe['date'] = daily_dataframe['date'].dt.date

    # Merge the hourly dataframe with the daily dataframe on the date
    merged_dataframe = pd.merge(hourly_dataframe, daily_dataframe, on='date', how='left')

    # Add weekday, month, and hour columns
    merged_dataframe['weekday'] = merged_dataframe['time'].dt.weekday
    merged_dataframe['month'] = merged_dataframe['time'].dt.month
    merged_dataframe['hour'] = merged_dataframe['time'].dt.hour
    
    # print("Merged dataframe")
    # print(merged_dataframe)

    # Convert to correct data types
    merged_dataframe['date'] = pd.to_datetime(merged_dataframe['date'])
    merged_dataframe['temperature'] = merged_dataframe['temperature'].astype(float)
    merged_dataframe['precipitation'] = merged_dataframe['precipitation'].astype(float)
    merged_dataframe['cloud_cover'] = merged_dataframe['cloud_cover'].astype(int)
    merged_dataframe['wind_speed_10m'] = merged_dataframe['wind_speed_10m'].astype(float)
    merged_dataframe['sunshine_duration'] = merged_dataframe['sunshine_duration'].astype(float)

    return merged_dataframe