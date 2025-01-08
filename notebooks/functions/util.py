import pandas as pd
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
from retry_requests import retry
from pathlib import Path

def plot_hourly_price_predictions(df: pd.DataFrame, date: str, file_path: str):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Filter the DataFrame for the specified date
    df['time'] = pd.to_datetime(df['time'])
    df_filtered = df[df['time'].dt.date == pd.to_datetime(date).date()]

    # Sort the DataFrame by time to ensure the steps are in the correct order
    df_filtered = df_filtered.sort_values(by='time')

    # Plot the predicted prices using a step plot
    ax.step(df_filtered['time'], df_filtered['predicted_price'], where='mid', label='Predicted Price', color='blue', linewidth=2)

    # Set the labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Predicted Price (EUR/MWh)')
    ax.set_title(f"Hourly Price Predictions for {date}")

    # Add a legend
    ax.legend(loc='upper right', fontsize='x-small')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Ensure everything is laid out neatly
    plt.tight_layout()

    # Save the figure, overwriting any existing file with the same name
    plt.savefig(file_path)
    return plt
