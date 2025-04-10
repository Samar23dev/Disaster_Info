import pandas as pd
import folium
import streamlit as st
import seaborn as sns
from streamlit_folium import st_folium
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_mongodb_connection():
    """Establish connection to MongoDB with error handling."""
    try:
        uri = os.getenv('MONGODB_URI')
        if not uri:
            raise ValueError("MongoDB URI not found in environment variables")
        
        client = MongoClient(uri)
        # Test the connection
        client.admin.command('ping')
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        st.error("Failed to connect to database. Please try again later.")
        return None

def main():
    """Display insights and analytics for disaster events."""
    try:
        # MongoDB connection
        client = get_mongodb_connection()
        if not client:
            return

        # Access the database and collection
        db = client[os.getenv('MONGODB_DB', 'newsfetcher')]
        collection = db[os.getenv('MONGODB_COLLECTION', 'geonews')]
        
        # Convert MongoDB cursor to DataFrame with error handling
        try:
            df = pd.DataFrame(list(collection.find()))
            if df.empty:
                st.warning("No data available in the database.")
                return
        except Exception as e:
            logger.error(f"Error fetching data from MongoDB: {str(e)}")
            st.error("Error fetching data. Please try again later.")
            return

        # Data cleaning and preprocessing
        try:
            df.drop_duplicates(subset='title', inplace=True)
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['Latitude', 'Longitude'])
            df = df[~df['url'].str.lower().str.contains('politics|yahoo|sports', na=False)]
            df = df[~df['title'].str.lower().str.contains('tool|angry', na=False)]
            df['date_only'] = df['timestamp'].dt.strftime('%Y-%m-%d')
            df.drop_duplicates(subset=['date_only', 'disaster_event', 'Location'], inplace=True)
            df.drop(columns=['date_only'], inplace=True)
            
            # Drop location_ner column if it exists
            if 'location_ner' in df.columns:
                df.drop(columns=['location_ner'], inplace=True)
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            st.error("Error processing data. Please try again later.")
            return

        # UI Components
        st.title("Disaster Insights and Analytics")
        
        # Date range filter
        st.sidebar.header('Filter Data')
        start_date_min = datetime.utcnow().date() - timedelta(days=30)
        start_date_past = datetime(2023, 1, 1)
        
        start_date = st.sidebar.date_input(
            "Start date",
            start_date_min,
            min_value=start_date_past,
            max_value=datetime.utcnow().date()
        )

        end_date = st.sidebar.date_input(
            "End date",
            datetime.utcnow().date(),
            min_value=start_date_past,
            max_value=datetime.utcnow().date()
        )

        # Date filtering
        start_date_utc = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_date_utc = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Filter dataframe
        filtered_df = df[(df['timestamp'] >= start_date_utc) & (df['timestamp'] <= end_date_utc)]
        
        if filtered_df.empty:
            st.subheader(":green[No Disaster data available after filtering based on the condition]")
            return

        # Disaster event distribution
        st.subheader("Disaster Event Distribution")
        event_counts = filtered_df['disaster_event'].value_counts().reset_index()
        event_counts.columns = ['Disaster Event', 'Count']
        
        fig = px.bar(
            event_counts, 
            x='Disaster Event', 
            y='Count',
            title="Distribution of Disaster Events",
            color='Disaster Event',
            labels={'Count': 'Number of Events', 'Disaster Event': 'Type of Disaster'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Location distribution
        st.subheader("Location Distribution")
        location_counts = filtered_df['Location'].value_counts().head(10).reset_index()
        location_counts.columns = ['Location', 'Count']
        
        fig = px.bar(
            location_counts, 
            x='Location', 
            y='Count',
            title="Top 10 Locations Affected by Disasters",
            color='Count',
            labels={'Count': 'Number of Events', 'Location': 'Location'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Time series analysis
        st.subheader("Disaster Events Over Time")
        daily_counts = filtered_df.groupby(filtered_df['timestamp'].dt.date).size().reset_index()
        daily_counts.columns = ['Date', 'Count']
        
        fig = px.line(
            daily_counts, 
            x='Date', 
            y='Count',
            title="Daily Disaster Events",
            labels={'Count': 'Number of Events', 'Date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Word cloud
        st.subheader("Word Cloud of Disaster Titles")
        try:
            text = ' '.join(filtered_df['title'].astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        except Exception as e:
            logger.error(f"Error generating word cloud: {str(e)}")
            st.warning("Could not generate word cloud. Please try again later.")
        
        # Map visualization
        st.subheader("Geographic Distribution of Disasters")
        try:
            map_center = (filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean())
            mymap = folium.Map(location=map_center, zoom_start=4, fullscreen_control=True)
            marker_cluster = MarkerCluster().add_to(mymap)
            
            for index, row in filtered_df.iterrows():
                popup_content = f"<a href='{row['url']}' target='_blank'>{row['title']}</a>"
                tooltip_content = f"{row['disaster_event']}, {row['Location']}"
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=tooltip_content
                ).add_to(marker_cluster)
            
            st_folium(mymap, width='100%', height=500)
        except Exception as e:
            logger.error(f"Error generating map: {str(e)}")
            st.warning("Could not generate map. Please try again later.")
        
        # Data table
        st.subheader("Disaster Events Data")
        columns_to_display = ['title', 'disaster_event', 'timestamp', 'source', 'url', 'Location']
        st.write(filtered_df[columns_to_display])
        
        logger.info("Insight page displayed successfully")
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()

