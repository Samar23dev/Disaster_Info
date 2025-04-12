import pandas as pd
import requests
import datetime
import spacy
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
import importlib.metadata
import time
from google.api_core import retry
from google.api_core.exceptions import ResourceExhausted

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('disaster_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Check google-generativeai version
try:
    genai_version = importlib.metadata.version('google-generativeai')
    logger.info(f"Using google-generativeai version: {genai_version}")
except importlib.metadata.PackageNotFoundError:
    logger.error("google-generativeai package not found. Please install it using: pip install google-generativeai")
    raise

# API Keys and Configuration
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '9026d49691d14f95bb9320730158b797')
NEWSAPI_ENDPOINT = 'https://newsapi.org/v2/everything'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MONGODB_URI = os.getenv('MONGODB_URI', "mongodb+srv://samarmittal59:Qwerty%40123@cluster0.raeompg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Configure Gemini API
try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
        
    # Simple configuration that we know works
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Initialize the model with the known working name
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Test the model with a simple prompt
    test_response = model.generate_content("Test connection")
    if test_response:
        logger.info("Gemini API configured and tested successfully")
    
except Exception as e:
    logger.error(f"Error configuring Gemini API: {str(e)}")
    raise

disaster_keywords = ['earthquake', 'flood', 'tsunami', 'hurricane', 'wildfire', 'forestfire', 'tornado', 'cyclone', 'volcano', 'drought', 'landslide', 'storm', 'blizzard', 'avalanche', 'heatwave']

# Load the spaCy English language model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model loaded successfully")
except OSError:
    logger.error("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    raise

# Initialize geocoder with a larger timeout
geolocator = Nominatim(user_agent="disaster_info_geocoder", timeout=20)

def fetch_live_data(keyword):
    """Fetch news data with improved error handling"""
    try:
        two_days_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=5)
        params = {
            'apiKey': NEWSAPI_KEY,
            'q': keyword,
            'from': two_days_ago.strftime('%Y-%m-%d'),
            'to': datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'relevancy'
        }
        
        response = requests.get(NEWSAPI_ENDPOINT, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get('articles', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for keyword {keyword}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_live_data: {str(e)}")
        return []

def pre_filter_articles(articles):
    """Pre-filter articles using NLP and keyword matching"""
    filtered_articles = []
    
    for article in articles:
        try:
            # Safely get title and description with proper error handling
            title = str(article.get('title', '')).lower()
            description = str(article.get('description', '')).lower()
            
            # Skip articles with empty titles
            if not title.strip():
                continue
                
            # Check for disaster keywords in title and description
            has_disaster_keyword = any(keyword.lower() in title or keyword.lower() in description 
                                     for keyword in disaster_keywords)
            
            # Use spaCy to check for disaster-related entities
            doc = nlp(title + " " + description)
            has_disaster_entity = any(ent.label_ in ['EVENT', 'FAC'] for ent in doc.ents)
            
            # If either condition is met, keep the article for further processing
            if has_disaster_keyword or has_disaster_entity:
                filtered_articles.append(article)
                
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            continue
    
    return filtered_articles

def process_articles_batch(articles, max_retries=3, initial_delay=1):
    """Process a batch of articles using Gemini API with rate limiting and retries"""
    if not articles:
        return []
        
    for attempt in range(max_retries):
        try:
            # Prepare a simpler batch prompt
            articles_text = "\n".join([
                f"Article {i+1}: {article['title']}"
                for i, article in enumerate(articles)
            ])
            
            prompt = f"""Analyze these news articles and classify each as either a disaster or not. 
            If it's a disaster, identify the type from this list: {', '.join(disaster_keywords)}.
            
            Articles:
            {articles_text}
            
            Return ONLY a JSON object with this exact format:
            {{
                "classifications": [
                    {{"title": "article title", "type": "disaster_type_or_Not a Disaster"}},
                    {{"title": "article title", "type": "disaster_type_or_Not a Disaster"}}
                ]
            }}
            """
            
            logger.info(f"Sending batch of {len(articles)} articles to Gemini")
            response = model.generate_content(prompt)
            classifications = response.text.strip()
            
            # Clean the response by removing markdown code block syntax
            if classifications.startswith('```json'):
                classifications = classifications[7:]  # Remove ```json
            if classifications.endswith('```'):
                classifications = classifications[:-3]  # Remove ```
            classifications = classifications.strip()
            
            # Parse the JSON response
            try:
                import json
                results = json.loads(classifications)
                processed_articles = []
                
                for classification in results.get('classifications', []):
                    title = classification.get('title', '')
                    disaster_type = classification.get('type', '')
                    
                    # Find the matching article
                    article = next((a for a in articles if a['title'] == title), None)
                    if article and disaster_type != "Not a Disaster" and disaster_type.lower() in [k.lower() for k in disaster_keywords]:
                        article['disaster_event'] = disaster_type.capitalize()
                        processed_articles.append(article)
                
                logger.info(f"Successfully processed {len(processed_articles)} disaster articles from batch")
                return processed_articles
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
                logger.error(f"Cleaned response: {classifications}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying batch processing (Attempt {attempt + 2}/{max_retries})")
                    continue
                return []
                
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                retry_delay = initial_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for rate limit. Error: {str(e)}")
                return []
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying batch processing (Attempt {attempt + 2}/{max_retries})")
                continue
            return []

def identify_disaster_event_keywords(title):
    """Fallback method using keyword matching"""
    if not title:
        return np.nan
        
    title_lower = title.lower()
    for keyword in disaster_keywords:
        if keyword.lower() in title_lower:
            return keyword.capitalize()
    return np.nan

def extract_location_ner(text):
    """Extract location entities using spaCy"""
    if not text:
        return []
        
    try:
        doc = nlp(text)
        location_ner_tags = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
        return list(set(location_ner_tags))  # Remove duplicates
    except Exception as e:
        logger.error(f"Error in NER processing: {str(e)}")
        return []

def get_coordinates(location):
    """Get coordinates with error handling"""
    if not location:
        return (np.nan, np.nan)
        
    try:
        location_info = geolocator.geocode(location, timeout=10)
        if location_info:
            return (location_info.latitude, location_info.longitude)
        return (np.nan, np.nan)
    except GeocoderTimedOut:
        logger.error(f"Geocoding timed out for {location}")
        return (np.nan, np.nan)
    except Exception as e:
        logger.error(f"Error geocoding {location}: {str(e)}")
        return (np.nan, np.nan)

def process_location_data(location_list):
    """Process location data into country, region, and city"""
    country, region, city = '', '', ''
    if len(location_list) >= 1:
        country = location_list[0]
    if len(location_list) >= 2:
        region = location_list[1]
    if len(location_list) >= 3:
        city = location_list[2]
    return country, region, city

def create_location(row):
    """Create a single location string from the most specific available location"""
    if row['City']:
        return row['City']
    elif row['Region']:
        return row['Region']
    elif row['Country']:
        return row['Country']
    return np.nan

def main(test_mode=False, max_test_batches=3):
    try:
        logger.info("Starting data collection process")
        all_live_data = []
        
        # Fetch articles for all keywords
        for keyword in disaster_keywords:
            logger.info(f"Processing keyword: {keyword}")
            live_data = fetch_live_data(keyword)
            if live_data:
                all_live_data.extend(live_data)
        
        if not all_live_data:
            logger.warning("No articles collected")
            return
            
        logger.info(f"Total articles collected: {len(all_live_data)}")
        
        # Pre-filter articles using NLP and keyword matching
        pre_filtered_articles = pre_filter_articles(all_live_data)
        logger.info(f"Articles after pre-filtering: {len(pre_filtered_articles)}")
        
        if not pre_filtered_articles:
            logger.warning("No potentially relevant articles found after pre-filtering")
            return
            
        # Process pre-filtered articles in batches
        batch_size = 10  # Reduced batch size to avoid timeouts
        processed_articles = []
        
        # Calculate total batches
        total_batches = (len(pre_filtered_articles) + batch_size - 1) // batch_size
        
        # If in test mode, limit the number of batches
        if test_mode:
            logger.info(f"TEST MODE: Processing only {max_test_batches} batches out of {total_batches} total batches")
            total_batches = min(max_test_batches, total_batches)
        
        for i in range(0, len(pre_filtered_articles), batch_size):
            current_batch = (i // batch_size) + 1
            if current_batch > total_batches:
                break
                
            batch = pre_filtered_articles[i:i + batch_size]
            logger.info(f"Processing batch {current_batch} of {total_batches}")
            processed_batch = process_articles_batch(batch)
            processed_articles.extend(processed_batch)
            
            # Add a small delay between batches to avoid rate limits
            time.sleep(1)
        
        if not processed_articles:
            logger.warning("No disaster articles found after Gemini processing")
            return
            
        # Create DataFrame and process data
        df = pd.DataFrame(processed_articles)
        logger.info(f"Final data collection: {len(df)} articles")
        
        # Data cleaning
        df.drop_duplicates(subset='title', inplace=True)
        df.dropna(subset=['disaster_event', 'source'], inplace=True)
        
        # Process locations
        df['location_ner'] = df['title'].apply(extract_location_ner)
        df = df[df['location_ner'].apply(len) > 0]
        
        # Split location data
        location_data = pd.DataFrame(df['location_ner'].apply(process_location_data).tolist(), 
                                   columns=['Country', 'Region', 'City'])
        df = pd.concat([df, location_data], axis=1)
        
        # Create location string and get coordinates
        df['Location'] = df.apply(create_location, axis=1)
        df = df.dropna(subset=['Location'])
        
        # Filter out non-disaster content - handle NaN values properly
        df = df[~df['url'].fillna('').str.lower().str.contains('politics|yahoo|sports|entertainment|cricket')]
        
        # Get coordinates
        df['Coordinates'] = df['Location'].apply(get_coordinates)
        df['Latitude'] = df['Coordinates'].apply(lambda x: x[0] if isinstance(x, tuple) and len(x) == 2 else np.nan)
        df['Longitude'] = df['Coordinates'].apply(lambda x: x[1] if isinstance(x, tuple) and len(x) == 2 else np.nan)
        df.drop('Coordinates', axis=1, inplace=True)
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        # Save to Excel
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_filename = f'disaster_data_{timestamp}.xlsx'
        df.to_excel(excel_filename, index=False)
        logger.info(f"Processed data saved to {excel_filename}: {len(df)} valid entries")
        
        # Save to MongoDB
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        db = client["newsfetcher"]
        collection = db["geonews"]
        
        try:
            data_list = df.to_dict(orient='records')
            result = collection.insert_many(data_list)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} documents into MongoDB")
        except Exception as e:
            logger.error(f"Error inserting data into MongoDB: {str(e)}")
        finally:
            client.close()
            
        logger.info("Data collection process completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    # Run in test mode with 3 batches
    main(test_mode=True, max_test_batches=300)