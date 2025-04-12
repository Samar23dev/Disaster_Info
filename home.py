import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
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

def get_custom_icon_path(disaster_event):
    """Get icon path for disaster event type."""
    icon_paths = {
        "Avalanche": "icons/avalanche.png",
        "Blizzard": "icons/blizzard.png",
        "Cyclone": "icons/cyclone.png",
        "Drought": "icons/drought.png",
        "Earthquake": "icons/earthquake.png",
        "Flood": "icons/flood.png",
        "Heatwave": "icons/heatwave.png",
        "Hurricane": "icons/hurricane.png",
        "Landslide": "icons/landslide.png",
        "Storm": "icons/storm.png",
        "Tornado": "icons/tornado.png",
        "Tsunami": "icons/tsunami.png",
        "Volcano": "icons/volcano.png",
        "Wildfire": "icons/wildfire.png",
    }
    return icon_paths.get(disaster_event, 'icons/default.png')

def get_disaster_color(disaster_event):
    """Get color for disaster event type."""
    color_map = {
        "Avalanche": "#8B4513",  # Brown
        "Blizzard": "#87CEEB",   # Sky Blue
        "Cyclone": "#4169E1",    # Royal Blue
        "Drought": "#DAA520",    # Goldenrod
        "Earthquake": "#FF4500", # Orange Red
        "Flood": "#1E90FF",      # Dodger Blue
        "Heatwave": "#FF6347",   # Tomato
        "Hurricane": "#000080",  # Navy
        "Landslide": "#A0522D",  # Sienna
        "Storm": "#4682B4",      # Steel Blue
        "Tornado": "#4B0082",    # Indigo
        "Tsunami": "#00CED1",    # Dark Turquoise
        "Volcano": "#8B0000",    # Dark Red
        "Wildfire": "#FF8C00",   # Dark Orange
    }
    return color_map.get(disaster_event, "#808080")  # Default gray

def main():
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
            
            # Add color column for visualization
            df['color'] = df['disaster_event'].apply(get_disaster_color)
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            st.error("Error processing data. Please try again later.")
            return

        # Sidebar date filter
        st.sidebar.markdown('<div class="card">', unsafe_allow_html=True)
        st.sidebar.markdown('<h3 style="color: #1E88E5; margin-bottom: 1rem;">Date Filter</h3>', unsafe_allow_html=True)
        
        start_date_min = datetime.utcnow().date() - timedelta(days=7)
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
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

        # Recent events in sidebar
        st.sidebar.markdown('<div class="card">', unsafe_allow_html=True)
        st.sidebar.markdown('<h3 style="color: #1E88E5; margin-bottom: 1rem;">Recent Key Events</h3>', unsafe_allow_html=True)
        
        # Filter recent events
        recent_events = df[df['disaster_event'].isin(["Earthquake", "Flood", "Cyclone", "Volcano"])]
        seven_days_ago = pd.Timestamp(datetime.utcnow() - timedelta(days=5), tz="UTC")
        recent_events = recent_events[recent_events['timestamp'] >= seven_days_ago]
        recent_events = recent_events.sort_values(by='timestamp', ascending=False)

        # Create marquee content
        marquee_content = ""
        for _, row in recent_events.iterrows():
            marquee_content += f"""
            <div style="margin-bottom: 15px; padding: 10px; border-left: 4px solid {row['color']}; background-color: #f8f9fa;">
                <div style="font-weight: bold; color: {row['color']}; margin-bottom: 5px;">{row['disaster_event']}</div>
                <a href="{row['url']}" target="_blank" style="text-decoration: none; color: #333;">{row['title']}</a>
                <div style="font-size: 0.8em; color: #666; margin-top: 5px;">{row['Location']} - {row['timestamp'].strftime('%Y-%m-%d')}</div>
            </div>
            """

        # Marquee HTML
        marquee_html = f"""
            <div class="marquee-container" onmouseover="stopMarquee()" onmouseout="startMarquee()">
                <div class="marquee-content">{marquee_content}</div>
            </div>
            <style>
                .marquee-container {{
                    height: 300px;
                    overflow: hidden;
                    border-radius: 5px;
                    background-color: white;
                }}
                .marquee-content {{
                    animation: marquee 40s linear infinite;
                    padding: 10px;
                }}
                @keyframes marquee {{
                    0%   {{ transform: translateY(10%); }}
                    100% {{ transform: translateY(-100%); }}
                }}
                .marquee-content:hover {{
                    animation-play-state: paused;
                }}
            </style>
            <script>
                function stopMarquee() {{
                    document.querySelector('.marquee-content').style.animationPlayState = 'paused';
                }}
                function startMarquee() {{
                    document.querySelector('.marquee-content').style.animationPlayState = 'running';
                }}
            </script>
        """
        st.sidebar.markdown(marquee_html, unsafe_allow_html=True)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

        # Date filtering
        start_date_utc = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_date_utc = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        filtered_df = df[(df['timestamp'] >= start_date_utc) & (df['timestamp'] <= end_date_utc)]

        # Display header
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h1 style="color: #1E88E5; text-align: center; margin-bottom: 1rem;">Global Disaster News Feed</h1>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Display news feed with improved styling
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Add download button
        if not filtered_df.empty:
            csv = filtered_df[['title', 'disaster_event', 'timestamp', 'source', 'url', 'Location']].to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name="disaster_data.csv",
                mime="text/csv",
                help="Click to download the current filtered data as CSV",
            )

        # Create news feed with improved styling
        for _, row in filtered_df.iterrows():
            st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: white;">
                    <div style="display: flex; align-items: start; gap: 15px;">
                        <div style="min-width: 80px; text-align: center;">
                            <img src="{get_custom_icon_path(row['disaster_event'])}" style="width: 40px; height: 40px;">
                            <div style="color: {row['color']}; font-weight: bold; font-size: 0.9em; margin-top: 5px;">
                                {row['disaster_event']}
                            </div>
                        </div>
                        <div style="flex-grow: 1;">
                            <h3 style="color: #333; margin: 0 0 10px 0; font-size: 1.1em;">{row['title']}</h3>
                            <div style="display: flex; justify-content: space-between; align-items: center; color: #666; font-size: 0.9em;">
                                <div>
                                    <span style="margin-right: 15px;">📍 {row['Location']}</span>
                                    <span style="margin-right: 15px;">📰 {row['source']}</span>
                                    <span>🕒 {row['timestamp'].strftime('%Y-%m-%d %H:%M')}</span>
                                </div>
                                <a href="{row['url']}" target="_blank" 
                                   style="background-color: {row['color']}; color: white; 
                                          padding: 5px 15px; text-decoration: none; 
                                          border-radius: 5px; font-size: 0.9em;">
                                    Read More
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
