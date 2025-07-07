from helperScripts import *
from Modules_check import *
# Configure the logger (do this once at the beginning of your script)
from hotels_scrapping import *
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.path.dirname(os.path.abspath(__file__))


os.getcwd()

# ********************************** Main Functionality **********************************
if __name__ == "__main__":
    # Read command-line arguments
    process_for = str(sys.argv[1] if len(sys.argv) > 1 else 1)
    process_for2 = str(sys.argv[2] if len(sys.argv) > 2 else 3)
    date_range = str(sys.argv[3] if len(sys.argv) > 3 else 2)

    # process_for = "1"  # Example: Category selection (1 for Hotels, 2 for Stocks, 3 for All)
    # process_for2 = "3"  # Example: Option selection (1 for ITC Kohinur, 2 for ITC Sonar, etc.)
    # date_range = "70" # Example: Option selection (1 for ITC Kohinur, 2 for ITC Sonar, etc.)
    

    # Importing the required modules
    config_path = "Config//config.json"

    config = getConfig(config_path)
    # Setting the Broswer
    setting_Param = config["settings"]
    browserObj = Parent(setting_Param["DRIVER"],
                        setting_Param["SCROLL_PAUSE_TIME"],
                        setting_Param["MAX_SCROLLS_OR_NEXT_PAGE"],
                        setting_Param["CHROME_OPTIONS"],
                        setting_Param["DRIVER_LOCATION"])
    ## Driver Settings##
    logger.info(f'Request Raised By:{(os.getlogin()).capitalize()}')
    # logger.info(f"Request Raised for the following stocks: {param}")
    driver_loc = bytes.fromhex(setting_Param["DRIVER_LOCATION"]).decode('utf-8')
    logger.info(driver_loc)
    ############ User Input ####################
    type_of_run = config['category_map']
    options = config['options']
    if process_for == "3":
        logger.info("Selected: ALL categories")
    elif process_for in options:
        category_name = type_of_run.get(process_for, "Unknown")
        item = options[process_for].get(process_for2, "Invalid Option")
        logger.info(f"Selected Category: {category_name}")
        logger.info(f"Selected Option: {item}")
    else:
        logger.warning("Invalid selection. Please try again.")
    # *********************** Path *****************************
    basePath = os.getcwd()
    webpath = os.path.join(basePath, config["output_path"], category_name)
    Stagging_path = os.path.join(basePath, config["Stagging_path"])
    finalPath = os.path.join(basePath, config["analysis_path"], category_name, item)
    try:
        shutil.rmtree(os.path.join(basePath, "Output"))
    except Exception as e:
        logger.error(f"Error while deleting path: {str(e)}")
    logger.info("*"*50)
    logger.info("TASK 1 has been started")
    logger.info("*"*50)
    if category_name == "Hotels":
        # Setting the Hotel Site
        run_type = config[category_name]
        if item == "ALL":
            hotel_sites = config["Hotels"]
            
            for site_name, details in hotel_sites.items():
                logger.info("Scraper has been started....")
                logger.info(f"Site Name: {site_name}")
                element_details = details["Class"]
                element_selector = element_details["element_selector"]
                ts_selector = element_details["ts_selector"]
                review_title = element_details["review_title"]
                review_text = element_details["review_text"]
                review_score = element_details["score"]
                next_page_selector = element_details["next_page_selector"]
                base_url = details["Base_URL"]
                logger.info(f"base_url: {base_url}")
                hotel_site = details["Hotels"]
                for hotel_name, url in hotel_site.items():
                    hotel_url = f"{base_url}{url}"
                    logger.info(f"Hotel Name: {hotel_name}")
                    obj = BookingDotCom(
                    browserObj, hotel_url, element_selector, ts_selector,
                    review_title, review_text, review_score, site_name,
                    hotel_name , next_page_selector
                )
                    # Calling the method to get the data
                    obj.get_the_data()
        else:
            hotel_sites = config["Hotels"]
            for site_name, details in hotel_sites.items():
                logger.info("Scraper has been started....")
                logger.info(f"Site Name: {site_name}")
                element_details = details["Class"]
                element_selector = element_details["element_selector"]
                ts_selector = element_details["ts_selector"]
                review_title = element_details["review_title"]
                review_text = element_details["review_text"]
                review_score = element_details["score"]
                next_page_selector = element_details["next_page_selector"]
                base_url = details["Base_URL"]
                logger.info(f"base_url: {base_url}")
                hotel_site = details["Hotels"]
                
                for hotel_name, url in hotel_site.items():
                    # print(f"eeHotel Name: {hotel_name}, Item: {item}")
                    if hotel_name != item:
                        continue
                    hotel_url = f"{base_url}{url}"
                    logger.info(f"Hotel Name: {hotel_name}")
                    obj = BookingDotCom(
                    browserObj, hotel_url, element_selector, ts_selector,
                    review_title, review_text, review_score, site_name,
                    hotel_name , next_page_selector
                )
                    # Calling the method to get the data
                    obj.get_the_data()
        logger.info("Scraper has been completed....")
        logger.info("Createing the File")
        df_hotels = convert_to_DataFrame(helperScripts.glb_all_comments, timestamp_format= "%B %d, %Y", user_defines_date=int(date_range))
        if len(df_hotels) != 0:
            logger.info("The data fetched completed from the website....")
            save_Comments(df_hotels, os.path.join(webpath, item), f"comments_{item}")
        else:
            logger.warning(f"No comments found for {item} in {category_name}. within the given date range.")
    elif category_name == "Stocks":
        browserObj = Parent(setting_Param["DRIVER"],
                        setting_Param["SCROLL_PAUSE_TIME"],
                        setting_Param["MAX_SCROLLS"],
                        setting_Param["CHROME_OPTIONS"],
                        setting_Param["DRIVER_LOCATION"])
    
        logger.info(f'Request Raise By:{(os.getlogin()).capitalize()}')
        # logger.info(f"Request Raised for the following stocks: {param}")
        driver_loc = bytes.fromhex(setting_Param["DRIVER_LOCATION"]).decode('utf-8')
        logger.info(driver_loc)
        ## User Details
        user_details = getUser_Input(config['UserInput'])
        # for stock_name, url in user_details.items():
        #     logger.info(f"Request Raised for the following stocks: {stock_name}")
        #     sitenam = url.split('/')[2] 
        #     if 'moneycontrol' in sitenam:
        #         param = config["MoneyControl"]
        #         # Site Config
        #         element_selector = param["element_selector"]
        #         ts_selector = param["ts_selector"] 
        #         author_selector = param["author_selector"]
        #         # Calling the class
        #         MC_Obj = Moneycontrolscraper(browserObj, url, element_selector, ts_selector, author_selector)
        #         MC_Obj.save_Comments(stock_name)
        #     else:
        #         logger.error(f"Error: Unsupported site '{sitenam}'")
    else:
        raise ValueError("Invalid category selected. Please choose a valid category.")

    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")
    # Move the file to the Analysis Directory
    try:
        pass
        # Clean Stagging Directory
        [os.remove(f) for f in glob.glob(os.path.join(Stagging_path, "*")) if os.path.isfile(f)]
        move_File_To_Analysis_Dir(webpath, Stagging_path)
    except Exception as e:
        logger.error(f"{str(e)}")
    logger.info("*"*50)
    logger.info("TASK 1 has been completed successfully")
    logger.info("*"*50)
    
    # Sentiment Analysis Start
    from sentimentAnalysis.sentimentGraph import *
    logger.info("*"*50)
    logger.info("TASK 2: Sentiment Analysis Started")
    logger.info("*"*50)
    try:
        logger.info(f"Final Path: {finalPath}")
        kickOffTheSentimentAnalysis(Stagging_path, finalPath)
    except Exception as e:
        logger.error(f"{str(e)}")
    
    logger.info("Process Completed......")
    # Delete Stagging Folder
    delete_folder(Stagging_path)
    star1 = "*"*50
    start2 = "*"*10
    logger.info(star1)
    logger.info(f"TASK 2 has been completed successfully")
    logger.info(star1)
    # logger.info("*"*10,"THE END","*"*10)
    logger.info("press any key to exit")