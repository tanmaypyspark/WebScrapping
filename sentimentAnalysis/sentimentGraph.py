import nltk
import pandas as pd
import numpy as np
import os, sys
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googletrans import Translator
import swifter
import logging
from tqdm.notebook import tqdm as notebook_tqdm
from langdetect import detect, DetectorFactory, LangDetectException
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Download Vader Package
nltk.download('vader_lexicon')
pd.options.mode.copy_on_write = True
analyzer = SentimentIntensityAnalyzer()

## Read .csv file
def read_file(filePath, format = 'csv'):
    
    if 'csv' in format:
        df = pd.read_csv(filePath)
    if '.json' in format:
        df = pd.read_json(filePath)
    if '.xlsx' in format:
        df = pd.read_excel(filePath)
    if '.txt' in format:
        df = pd.read_csv(filePath, delimiter = '\t')
    return df

def write_file(filePath, df, format = 'csv'):
    
    if 'csv' in format:
        df.to_csv(filePath, index = False)
    if '.json' in format:
        df.to_json(filePath)
    if '.xlsx' in format:
        df.to_excel(filePath, index = False)
    if '.txt' in format:
        df.to_csv(filePath, index = False, sep = '\t')

def translatorTOENG(df, column_name):
    #Create Translator object
    trans = Translator()
    
    # Apply translation to each row in the specified column
    df['Translated_Text'] = df[column_name].swifter.apply(
        lambda text: trans.translate(text, src='hi', dest='en').text if pd.notnull(text) else text
    )
    # Drop columns:
    df = df.drop(column_name, axis=1)
    
    df.rename(columns={'Translated_Text': column_name}, inplace=True)
    
    
    return df

def detect_language(text):
    try:
        # Check if the text is valid
        if pd.isnull(text) or text.strip() == "":
            return "unknown"  # Return "unknown" for empty or invalid text
        return detect(text)
    except LangDetectException:
        return "unknown"  # Return "unknown" if language detection fails

# def detect_language(text):
#     return detect(text)


    
def sentiment_Analyzer(df):
    # Apply Sentiment Analysis to the 'Comment' column
    try:
        if 'Comment' in df.columns:
            ## Fill the NaN values with empty string
            df['Comment'] = df['Comment'].fillna('')
            
            ## Apply Sentiment Analysis
            df['Sentiment_Score'] = df['Comment'].swifter.apply(lambda x: analyzer.polarity_scores(x)['compound'])
            
            df["Sentiment_Label"] = np.where(df["Sentiment_Score"] >= 0.2, 'Positive', (np.where(df["Sentiment_Score"] < 0, 'Negative', 'Neutral')))
            return df
        else:
            logger.error("'Comment' column not found in the DataFrame.")
        
    except Exception as e:
        logger.error(f"An error occurred during Sentiment Analysis: {e}")
        sys.exit(1)

def kickOffTheSentimentAnalysis(basepath, finalPath):
    ''' This Function is use to Kick Off the Sentiment Analysis'''
    logger.info("Starting Sentiment Analysis...")
    
    for file in os.listdir(basepath):
        logger.info(f"Sentiment Analysis Starts For: {file}")
        removeFromFileName = '_'.join(file.split('_')[-2:])
        finalFileName = file.replace(f"_{removeFromFileName}", '.csv').replace('comments','Sentiment_Analysis')
        logger.info(f"Final File Name: {finalFileName}")
        # Read the file
        filepath = os.path.join(basepath, file)
        df_data = read_file(filepath)
        list_of_columns = df_data.columns.tolist()
        # Translate the comments to English, If any Hinlish comments are present
        df_data['Language'] = df_data['Comment'].apply(detect_language)
        # Filter non -English comments
        df_translate_Not_required = df_data[df_data['Language'] == 'en']
        df_UNKNOW = df_data[df_data['Language'] == "unknown"]
        df_translate_required = df_data[df_data['Language'] != 'en']
        # Translate the comments to English
        # print(df_translate_required)
        df_translated = translatorTOENG(df_translate_required, 'Comment')
        #Merge the dataframes 
        df_merged = pd.concat([df_translate_Not_required, df_translated, df_UNKNOW], ignore_index=True, sort=False)
        
        # df_Final
        df_Final = df_merged[list_of_columns].copy()
        # Apply Sentiment Analysis
        df_sem_analyzer = sentiment_Analyzer(df_Final)
        # Final Column Selection
        list_of_columns.remove('Timestamp')
        df_F = df_sem_analyzer[list_of_columns + ['Sentiment_Score', 'Sentiment_Label', 'Timestamp']].copy()
        df_F = df_F.sort_values(by=['Timestamp', 'Sentiment_Score','Sentiment_Label'], ascending=[False, True, True])
        if not os.path.exists(finalPath):
            os.makedirs(finalPath)
        df_F.to_csv(os.path.join(finalPath, finalFileName), index = False)
