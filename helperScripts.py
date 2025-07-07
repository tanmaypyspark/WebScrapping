from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
import logging
import os
import json
import sys
import glob
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
global glb_all_comments
glb_all_comments = []
# # ******** Environment Setup ********
# if preSetupCheck():
#     logger.info("All modules are available.")
# else:
#     logger.error("Error: Required modules are not available.")
# ***********************************

from webScrapping import *
import shutil
# from datetime import datetime




class Parent():
    def __init__(self, driver, scroll_time, max_scroll, chrome_options, driver_location):
        Parent.DRIVER = driver
        Parent.SCROLL_PAUSE_TIME = scroll_time
        Parent.MAX_SCROLLS = max_scroll
        Parent.CHROME_OPTIONS = chrome_options
        Parent.DRIVER_LOCATION = driver_location

# Get the Config from a JSON file
def getConfig(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        logger.exception(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError:
        logger.exception(f"Error: Invalid JSON format in {filepath}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return None

# Get user input from a configuration file
def getUser_Input(filename):
    """Reads a config file and returns a dictionary of stock names and URLs."""
    config_data = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace
                if line:  # Skip empty lines
                    try:
                        stock_name, url = line.split(': ', 1)  # Split at the first ': '
                        config_data[stock_name] = url
                    except ValueError:
                        logger.warn(f"Invalid line in config file: {line}")
    except FileNotFoundError:
        logger.error(f"Config file '{filename}' not found.")
    return config_data

# Get the Date Range
def getDateRange(user_defines_date:int):
    ''' Get the date range based on user input for days back from today '''
    try:
        # days_back = int(input())

        if user_defines_date < 0:
            raise ValueError("You must enter a non-negative number.")

        # Get today's date
        today = datetime.datetime.now().date()
        current_date = today.strftime('%Y-%m-%d')

        # Subtract the offset
        previous_date = (today - datetime.timedelta(days=user_defines_date)).strftime('%Y-%m-%d')
        logger.info(
            f"📅 Date from {previous_date} to {current_date}")
        return previous_date, current_date

    except ValueError as e:
        print(f"⚠️ Invalid input: {e}")

          
def convert_to_DataFrame(list_data: list, timestamp_format: str = '%d-%m-%Y %H:%M', user_defines_date:int = 2) -> pd.DataFrame:
    ''' Convert List to a pandas dataframe'''
    df = pd.DataFrame(list_data)
    df = df.drop_duplicates()
    
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format=timestamp_format, errors='coerce')
    # # Fill rows with NaT (Not a Time) values in 'Timestamp'
    latest_timestamp = df['Timestamp'].max()
    df['Timestamp'] = df['Timestamp'].fillna(latest_timestamp)
    # df = df.dropna(subset=['Timestamp'])
    # User define Data filters
    previous_date, today = getDateRange(user_defines_date)
    df = df[
        (df["Timestamp"] >= pd.to_datetime(previous_date)) &
        (df["Timestamp"] <= pd.to_datetime(today))
    ]
    # Sort by timestamp in descending order (latest first)
    df = df.sort_values(by='Timestamp', ascending=False)
    return df

def save_Comments(df: pd.DataFrame, scrapper_type: str, file_name: str):
        ''' Save the comments to a csv file'''
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        path = scrapper_type.replace(' ', '').replace('  ','')
        logger.info(f"Saving comments to CSV file at {path}...")
        if not os.path.exists(path):
            os.makedirs(path)
        df.to_csv(f"{path}/{file_name.replace(' ', '').replace('  ','')}_{timestamp}.csv", index=False) #BASE_PATH + "comments.csv"
        logger.info(f"File has been generated successfully!!")


def check_datatime_format():
    date_string = "July 11, 2024"

    # List of possible formats
    formats = [
        "%B %d, %Y",  # Example: July 11, 2024
        "%d-%m-%Y",   # Example: 11-07-2024
        "%Y/%m/%d",   # Example: 2024/07/11
    ]

    # Detect the format
    for fmt in formats:
        try:
            parsed_date = datetime.datetime.strptime(date_string, fmt)
            print(f"Detected format: {fmt}")
            break
        except ValueError:
            continue


def move_File_To_Analysis_Dir(basepath, analysis_path):
    ''' This Function is use to move the file from output to Analysis Directory'''
    for dir in os.listdir(basepath):
        # Initialize variables to track the latest file
        latest_file = None
        latest_time = 0
        for file in os.listdir(os.path.join(basepath, dir)):
            print(file)
            file_path = os.path.join(basepath, dir, file)
            # Get the last modification time of the file
            timestamp = os.path.getmtime(file_path)
            # Update the latest file if this file is newer
            if timestamp > latest_time:
                latest_time = timestamp
                latest_file = file
            
        if latest_file:
            readable_time = datetime.datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M:%S')
            # Ensure the analysis directory exists
            os.makedirs(analysis_path, exist_ok=True)
            # Move the file
            shutil.copy(os.path.join(basepath, dir, file), analysis_path)
            logger.info(f"Copy {latest_file} to {analysis_path}")
        else:
            logger.warning(f"No files found in directory: {os.path.join(basepath, dir)}")


def delete_folder(folder_path):
    """
    Deletes the specified folder and all its contents.

    Args:
        folder_path: The path to the folder to delete.
    """
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            logger.info(f"Deleted folder: {folder_path}")
        except Exception as e:
            logger.error(f"Error deleting folder {folder_path}: {e}")
    else:
        logger.warning(f"Folder does not exist: {folder_path}")
