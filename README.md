# Electricity Price Forecasting

This project builds an Electricity Price Forecasting Service to predict hourly electricity prices for the regions SE3 (Stockholm area) and SE4 (Malmö). The service uses an XGBoostregressor to provide predictions for the hourly electricity spot price up to 5 days in advance.


- **Daily Predictions:** https://eliasschuhmacher.github.io/ML_Project_Electricity/

## Project Overview

The goal of this project is to forecast hourly electricity prices for different regions (SE3 and SE4) using historical data and weather information. The predictions are visualized and made available through a web interface hosted on GitHub Pages.

## Features

- **Hourly Price Predictions**: Predicts hourly electricity prices for the next few days.
- **Region-Specific Forecasts**: Provides forecasts for different regions (SE3 and SE4).
- **Visualization**: Displays the predictions in a user-friendly format using plots.
- **GitHub Pages**: Hosts the prediction plots on GitHub Pages for easy access.

## Data Sources

The project uses the following data sources:
- **Historical Electricity Prices**: Historical data of electricity prices for the regions SE3 and SE4. Retrieved from https://www.energidataservice.dk/tso-electricity/elspotprices 
- **Time factors**: Time of day, weekday, month
- **Weather Data**: Temperature, precipitation, cloud cover, wind speed, and sunshine duration. Retrieved from open-meteo.com
- **Current Electricity Prices**: New electricity prices are retrived on a daily basis from https://www.elprisetjustnu.se/elpris-api

## Model

The project uses an XGBoost regression model to predict future electricity prices based on historical data and weather information. The model is trained on past data and used to make predictions for the next few days.

## Visualization

The predictions are visualized using Matplotlib and displayed on a web page hosted on GitHub Pages. The plots show the hourly price predictions for each region, making it easy to understand the forecasted prices.
