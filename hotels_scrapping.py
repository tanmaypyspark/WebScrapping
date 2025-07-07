from helperScripts import *

import helperScripts
logger.info("Importing the required modules...")

class BookingDotCom:
    # global all_comments
    # all_comments = []
    def __init__(
        self, parent_instance, url, element_selector, ts_selector = '',
        review_title = '', review_text = '', review_score = '', hotel_site = '',
        hotel_name = '', next_page_selector = '', nested_div_selector = ''
        ):
        self.url = url
        self.element_selector = element_selector # This is the comment selector
        self.nested_div_selector = nested_div_selector
        self.timeStamp_selector = ts_selector # This is the timestamp selector
        # self.cmd_selector = author_selector # This is the author selector
        self.review_title = review_title # This is the review title selector
        self.review_text = review_text
        self.review_score = review_score
        self.hotel_site = hotel_site # This is the hotel site selector
        self.hotel_name = hotel_name
        self.next_page_selector = next_page_selector # This is the next page selector
        # self.glb_all_comments = glb_all_comments
        # *************************
        
        # *************************
        
        # ****************************************************
        BookingDotCom.DRIVER = parent_instance.DRIVER
        BookingDotCom.SCROLL_PAUSE_TIME = parent_instance.SCROLL_PAUSE_TIME #seconds
        BookingDotCom.MAX_SCROLLS = parent_instance.MAX_SCROLLS
        BookingDotCom.CHROME_OPTIONS = parent_instance.CHROME_OPTIONS
        BookingDotCom.DRIVER_LOCATION = parent_instance.DRIVER_LOCATION
        # ****************************************************
        self.driver_loc = bytes.fromhex(BookingDotCom.DRIVER_LOCATION).decode('utf-8')
        '''Start the Scraper'''
        
    def __find_Booking_Comments(self, soup):
        ''' Convert the comments to a pandas dataframe'''
        # all_comments = []
        for comment_element in soup.find_all("h4", class_=self.element_selector):
            # Get the Review Title (text inside the <h4> tag)
            review_title = comment_element.get_text(strip=True)

            # Get the Timestamp
            get_ts = comment_element.find_previous("div", class_=self.timeStamp_selector)  # Replace with your timestamp class
            timestamp = get_ts.get_text(strip=True) if get_ts else "N/A"

            # Get the Review Text
            get_text = comment_element.find_previous("div", class_= self.review_text)
            review_text = "N/A"

            if get_text:
                # Find the nested <span> tag inside the <div>
                nested_span = get_text.find("span")
                review_text = nested_span.get_text(strip=True) if nested_span else "N/A"
            # Review
            review = f"{review_title}{review_text}"
            # Filter out predefined patterns or unwanted comments
            # unwanted_phrases = ["Dear Guest", "Namaste", "Thank you for sharing"]
            # if any(phrase in review_text for phrase in unwanted_phrases):
            #     continue  # Skip this comment if it contains unwanted phrases

            # Get the Score
            unwanted_score = ["Rated very good"]
            get_score = comment_element.find_previous("div", class_=self.review_score)
            review_score = get_score.get_text(strip=True) if get_score else "N/A"
            if any(phrase in review_score for phrase in unwanted_score):
                review_score = "Scored 10"
            

            # Get the Author
            # get_author = comment_element.find_previous("div", class_="b08850ce41 f546354b44")
            # author = get_author.get_text(strip=True) if get_author else "N/A"

            # Get the Country
            # get_country = comment_element.find_previous("span", class_="d838fb5f41 aea5eccb71")
            # country = get_country.get_text(strip=True) if get_country else "N/A"

            # Get the Room Type
            # get_room_type = comment_element.find_previous("div", class_="c5eb966161")
            # room_type = get_room_type.get_text(strip=True) if get_room_type else "N/A"
            # print("Herrrrrrrrrrrrrrrrr")
            # List
            helperScripts.glb_all_comments.append(
                {
                    "Hotel_Name": self.hotel_name, "Timestamp": timestamp.replace('Reviewed: ', ''),
                    "Comment": review, "Review_Score": review_score.replace('Scored',''),
                    "Site": self.hotel_site
                })
            # print({
            #         "Timestamp": timestamp.replace('Reviewed: ', ''), "Review": review_title,
            #         "Review_Score": review_score.replace('Scored',''),
            #     })
        
    def __find_Agoda_Comments(self, soup):
        # logger.info("Finding TripAdvisor Comments...")
        # print(soup)
        for div in soup.find_all("div", class_=self.element_selector):
            # print(div.find("div", class_="Review-comment-reviewer"))
            # nested_div = div.find("div", class_="Review-comment-reviewer")
            # nested_div_review = div.find("div", class_=self.nested_div_selector)

            # Author and COuntry
            # if nested_div.get("data-info-type") == "reviewer-name":
            #     reviewer_strong = nested_div.find("strong")
            #     country_span = nested_div.find_all("span")[-1]
                # review_title = nested_div.find_all("group-name")
                # reviewer_name = reviewer_strong.get_text(strip=True) if reviewer_strong else "N/A"
                # country_name = country_span.get_text(strip=True) if country_span else "N/A"
            # Review Score
            review_score = div.find("div", class_=self.review_score).get_text(strip=True)
            # Review text and timestamp
            review_comment = div.find("div", class_=self.review_text).get_text(strip=True).replace('“', '').replace('”', ', ').strip()
            review_timestamp = div.find("div", class_=self.timeStamp_selector).get_text(strip=True).replace('Reviewed: ', '')
            helperScripts.glb_all_comments.append(
                {
                    "Hotel_Name": self.hotel_name, "Timestamp": review_timestamp,
                    "Comment": review_comment, "Review_Score": review_score.replace('Scored',''),
                    "Site": self.hotel_site                    
                })
    
    def click_next_reviews_page(self, driver, next_button_selector):
        try:
            # Wait for the button to be visible and clickable
            next_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(@aria-label, '{next_button_selector}') or contains(text(), '{next_button_selector}')]"))
            )

            # Scroll it into view first
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.5)  # Let layout stabilize

            # Try to click using ActionChains for more robustness
            ActionChains(driver).move_to_element(next_button).click().perform()
            logger.info("✅ Moved to next reviews page.")

        except ElementClickInterceptedException as e:
            logger.warning("❌ ElementClickInterceptedException: Something's blocking the button.")
        except Exception as e:
            logger.warning(f"❌ Could not click next reviews page: {e}")
    
    def __scrape_infinite_scroll(self):
        """Scrapes data from a page with infinite scrolling."""
        # logger.info(f"Opening the {self.url}...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
        chrome_options.add_argument("--disable-web-security")       # Disable web security
        chrome_options.add_argument("--allow-insecure-localhost")   # Allow insecure localhost connections
        chrome_options.add_argument(BookingDotCom.CHROME_OPTIONS)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Fetch the data from the website....")
        # Set the driver location
        try:
            if self.hotel_site not in ['Booking.com', 'Agoda']:
                raise ValueError("Unsupported hotel site. Supported sites are: Booking.com, Agoda.")
            driver.get(self.url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            # print("hotel_site", self.hotel_site)
            if self.hotel_site == 'Booking.com':
                self.__find_Booking_Comments(soup)
            elif self.hotel_site == 'Agoda':
                self.__find_Agoda_Comments(soup)
            # Go to the page to load all content
            scroll_count = 0
            # print("BookingDotCom.MAX_SCROLLS", BookingDotCom.MAX_SCROLLS)
            while scroll_count < BookingDotCom.MAX_SCROLLS:
                self.click_next_reviews_page(driver, self.next_page_selector)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                if self.hotel_site=='Booking.com':
                    self.__find_Booking_Comments(soup)
                elif self.hotel_site=='Agoda':
                    self.__find_Agoda_Comments(soup)
                scroll_count += 1
        except Exception as e:
            logger.error(f"{e}")
            return None
        finally:
            logger.info(f"Total Comments Found: {len(helperScripts.glb_all_comments)}")
            driver.quit()
    # jdksb
    def get_the_data(self):
        ''' Get the data from the website'''
        # self.__scrape_infinite_scroll()
        return self.__scrape_infinite_scroll() #self.glb_all_comments #self.__find_TripAdvisor_Comments(self.__scrape_infinite_scroll())
        # return convert_to_DataFrame(helperScripts.glb_all_comments, timestamp_format= "%B %d, %Y") 


############################# Main ##############################

  


# hotel_details = config[hotel_site]["Class"]





# base_url_trp = config["TripAdvisor"]['Base_URL']



# # TripAdvisor Details
# # hotel_details = config["Booking.com"]["Class"]



# hotel_url = config["TripAdvisor"]['Hotels']
# base_url_trp = config["TripAdvisor"]['Base_URL']
# print(hotel_details)
# print('-------')
# print(hotel_url)
# for hotel, url in hotel_url.items():
#     hotel_url = f"{base_url_trp}{url}"
# hotel_name = "ITC Kohenur, a Luxury Collection Hotel, Hyderabad"
# # hotel_url = "https://www.agoda.com/itc-kohenur-a-luxury-collection-hotel-hyderabad/hotel/hyderabad-in.html?countryId=35&finalPriceView=1&isShowMobileAppPrice=false&cid=1844104&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2025-07-14&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=1&showReviewSubmissionEntry=false&currencyCode=INR&isFreeOccSearch=false&los=1&searchrequestid=fc71c9be-d832-4577-93ec-20c18405316b&ds=YeMbbwKLV7gcoKJY"
# print(f"Hotel: {hotel_name}, URL: {hotel_url}")

# # Hotel
# hotel_url = "https://www.booking.com/hotel/in/itc-kohenur-a-luxury-collection-hyderabad.html#tab-reviews"

# element_selector = hotel_details["element_selector"]
# ts_selector = hotel_details["ts_selector"] 
# author_selector = hotel_details["review_author"]
# next_page_selector = hotel_details["next_page_selector"]
# # print(user_details)
# print('... calling BookingDotCom ...')
# obj = BookingDotCom(browserObj, hotel_url, element_selector, ts_selector, author_selector, '', '', '', hotel_site, hotel_name , next_page_selector)
# data = obj.get_the_data()
# parent_instance, url, element_selector, ts_selector = '',
#         author_selector = '', review_title = '', review_text = '',
#         review_score = '', hotel_site = '', hotel_name = '', next_page_selector = ''
# save_Comments(obj.get_the_data(), "Booking.com", "ITC Kohenur")
