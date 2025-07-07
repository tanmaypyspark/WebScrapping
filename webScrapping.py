
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Moneycontrolscraper:
    
    def __init__(self, parent_instance, url, element_selector, ts_selector, author_selector):
        self.url = url
        self.element_selector = element_selector # This is the comment selector
        self.timeStamp_selector = ts_selector # This is the timestamp selector
        self.cmd_selector = author_selector # This is the author selector
        # ****************************************************
        Moneycontrolscraper.DRIVER = parent_instance.DRIVER
        Moneycontrolscraper.SCROLL_PAUSE_TIME = parent_instance.SCROLL_PAUSE_TIME #seconds
        Moneycontrolscraper.MAX_SCROLLS = parent_instance.MAX_SCROLLS
        Moneycontrolscraper.CHROME_OPTIONS = parent_instance.CHROME_OPTIONS
        Moneycontrolscraper.DRIVER_LOCATION = parent_instance.DRIVER_LOCATION
        # ****************************************************
        self.driver_loc = bytes.fromhex(Moneycontrolscraper.DRIVER_LOCATION).decode('utf-8')
        '''Start the Scraper'''
        logger.info("Scraper has been started....")
        # logger.info(self.driver_loc)
                
    def __convert_time_to_datetime(self, time_str):
        """Converts relative or absolute time string to 'DD-MM-YYYY HH:MM' format."""
        try:
            if "mins" in time_str or "secs" in time_str:
                parts = time_str.split()
                minutes = 0
                seconds = 0

                if "mins" in time_str:
                    minutes = int(parts[0])
                if "secs" in time_str:
                    if "mins" in time_str:
                        seconds = int(parts[2])
                    else:
                        seconds = int(parts[0])

                now = datetime.datetime.now()
                time_delta = datetime.timedelta(minutes=minutes, seconds=seconds)
                past_time = now - time_delta
                return past_time.strftime("%d-%m-%Y %H:%M")

            else:
                # Absolute time (e.g., "10:12 AM Feb 12th" or "7:29 AM Aug 28th")
                time_str = time_str.replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")  # Remove suffixes
                now = datetime.datetime.now()

                # Try parsing with the current year
                try:
                    dt_object = datetime.datetime.strptime(time_str + f" {now.year}", "%I:%M %p %b %d %Y")
                except ValueError:
                    # If parsing fails, check if it's a leap year issue
                    if "Feb 29" in time_str:
                        try:
                            # Try parsing with the previous leap year
                            leap_year = now.year - (now.year % 4)
                            dt_object = datetime.datetime.strptime(time_str + f" {leap_year}", "%I:%M %p %b %d %Y")
                        except ValueError:
                            logger.warning(f"Invalid time string: {time_str}")
                            return None
                    else:
                        logger.warning(f"Invalid time string: {time_str}")
                        return None

                # Check if the parsed date is in the future. If so, subtract one year.
                if dt_object > now:
                    dt_object = datetime.datetime.strptime(time_str + f" {now.year - 1}", "%I:%M %p %b %d %Y")

                return dt_object.strftime("%d-%m-%Y %H:%M")

        except ValueError:
            logger.warning(f"Invalid time string: {time_str}")
            return None  # Return None if the input string is invalid
    
    def __scrape_infinite_scroll(self):
        """Scrapes data from a page with infinite scrolling."""
        logger.info(f"Opening the {self.url}...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
        chrome_options.add_argument("--disable-web-security")       # Disable web security
        chrome_options.add_argument("--allow-insecure-localhost")   # Allow insecure localhost connections
        chrome_options.add_argument(Moneycontrolscraper.CHROME_OPTIONS)
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Fetch the data from the website....")
        try:
            driver.get(self.url)

            # Wait for initial content to load
            WebDriverWait(driver, Moneycontrolscraper.DRIVER).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'.{self.element_selector}'))
            )

            scroll_count = 0
            while scroll_count < Moneycontrolscraper.MAX_SCROLLS:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait for new content to load
                time.sleep(Moneycontrolscraper.SCROLL_PAUSE_TIME)

                # Check if we've reached the end (optional, but helpful)
                # You might need to adjust this check based on your website's behavior
                try:
                    # Example: If a specific element disappears when all content is loaded
                    if not driver.find_elements(By.CSS_SELECTOR, "/html"):
                        logger.info("Reached end of content.")
                        break
                except:
                    pass #if the check fails, just continue scrolling

                scroll_count += 1

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            logger.info("The data fetched completed from the website....")
            return soup

        except Exception as e:
            logger.error(f"{e}")
            return None
        finally:
            driver.quit()
    
    def get_the_data(self):
        ''' Get the data from the website'''
        return self.__scrape_infinite_scroll()
    
    def __find_Comments(self, stock_name):
        ''' Find All the comments in the page'''
        elements = self.__scrape_infinite_scroll()
        logger.info("Find all the comments in the page....")
        comments = []
        all_comments = []

        for comment_element in elements.find_all("div", class_= self.element_selector):  # Replace class name
            # Get the comment
            comment_text = comment_element.get_text(strip=True)
            #Get the timestamp
            get_ts = comment_element.find_previous("div", class_= self.timeStamp_selector) # Replace with your timestamp class
            # Get the Author
            author = comment_element.find_previous("div", class_= self.cmd_selector).text.strip()
            if get_ts:
                timestamp_text = self.__convert_time_to_datetime(get_ts.find("div").text.strip().replace("schedule", ""))
            else:
                timestamp_text = "Timestamp not found"

            all_comments.append({"Stock": stock_name, "Comment": comment_text,'Commented By':author, "Timestamp": timestamp_text})
        
        logger.info("Successfully grab the Data!!")
        
        return all_comments
    
    def __Convert_to_DataFrame(self, stock_name):
        ''' Convert the comments to a pandas dataframe'''
        all_comments = self.__find_Comments(stock_name)
        df = pd.DataFrame(all_comments)
        df = df.drop_duplicates()
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M', errors='coerce')
        # # Fill rows with NaT (Not a Time) values in 'Timestamp'
        latest_timestamp = df['Timestamp'].max()
        df['Timestamp'] = df['Timestamp'].fillna(latest_timestamp)
        # df = df.dropna(subset=['Timestamp'])

        # Sort by timestamp in descending order (latest first)
        df = df.sort_values(by='Timestamp', ascending=False)
        return df
    
    def show_Comments(self, stock_name):
        ''' Display all the comments in the page'''
        data = self.__Convert_to_DataFrame(stock_name)
        logger.info("************* The DATA *************")
        logger.info(data)
    
    def check_dir(self, path):
        ''' Check the directory'''
        if not os.path.exists(path):
            os.makedirs(path)
    
    def save_Comments(self, stock_name):
        ''' Save the comments to a csv file'''
        data = self.__Convert_to_DataFrame(stock_name)
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        path = f"Output/WebData/{stock_name.replace(' ', '').replace('  ','')}/"
        self.check_dir(path)
        data.to_csv(f"{path}/comments_{stock_name.replace(' ', '').replace('  ','')}_{timestamp}.csv", index=False) #BASE_PATH + "comments.csv"
        logger.info(f"File has been generated successfully!!")
