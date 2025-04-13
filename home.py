import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

# Configure logging and load environment variables
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

def get_mongodb_connection():
    """Establish connection to MongoDB with error handling."""
    try:
        uri = os.getenv('MONGODB_URI')
        if not uri:
            raise ValueError("MongoDB URI not found in environment variables")
        client = MongoClient(uri)
        client.admin.command('ping')
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        st.error("Failed to connect to database. Please try again later.")
        return None

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
        # MongoDB connection and data retrieval
        client = get_mongodb_connection()
        if not client:
            return

        db = client[os.getenv('MONGODB_DB', 'newsfetcher')]
        collection = db[os.getenv('MONGODB_COLLECTION', 'geonews')]
        
        # Get and process data
        df = pd.DataFrame(list(collection.find()))
        if df.empty:
            st.warning("No data available in the database.")
            return

        # Basic data cleaning
        df.drop_duplicates(subset='title', inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        # Add color column for visualization
        df['color'] = df['disaster_event'].apply(get_disaster_color)
        
        # Sidebar filters
        st.sidebar.title("Filters")
        start_date = st.sidebar.date_input(
            "Start date",
            datetime.utcnow().date() - timedelta(days=7)
        )
        end_date = st.sidebar.date_input(
            "End date",
            datetime.utcnow().date()
        )
        
        # Add disaster type filter
        all_disaster_types = sorted(df['disaster_event'].unique().tolist())
        
        # Add "All" option to the disaster types
        disaster_types_with_all = ["All"] + all_disaster_types
        
        selected_disaster_types = st.sidebar.multiselect(
            "Disaster Types",
            options=disaster_types_with_all,
            default=["All"],
            help="Select disaster types to display in the news feed. Choose 'All' to see all disaster types."
        )
        
        # If "All" is selected, use all disaster types
        if "All" in selected_disaster_types:
            selected_disaster_types = all_disaster_types

        # Convert dates to UTC timestamps for comparison
        start_date_utc = pd.Timestamp(start_date).tz_localize('UTC')
        end_date_utc = pd.Timestamp(end_date).tz_localize('UTC') + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

        # Recent events in sidebar
        st.sidebar.title("Recent Key Events")
        five_days_ago = pd.Timestamp.utcnow() - pd.Timedelta(days=5)
        recent_events = df[
            (df['disaster_event'].isin(["Earthquake", "Flood", "Cyclone", "Volcano"])) &
            (df['timestamp'] >= five_days_ago)
        ].sort_values(by='timestamp', ascending=False)

        # Create a vertical scrolling marquee for recent events
        if not recent_events.empty:
            marquee_content = ""
            for _, row in recent_events.iterrows():
                marquee_content += f"""
                <div style="margin-bottom: 15px; padding: 10px; border-left: 4px solid {row['color']}; background-color: #f8f9fa;">
                    <div style="font-weight: bold; color: {row['color']}; margin-bottom: 5px;">{row['disaster_event']}</div>
                    <a href="{row['url']}" target="_blank" style="text-decoration: none; color: #333;">{row['title']}</a>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">📍 {row['Location']} - {row['timestamp'].strftime('%Y-%m-%d')}</div>
                </div>
                """

            # Marquee HTML with vertical scrolling
            marquee_html = f"""
                <div class="marquee-container" style="height: 300px; overflow: hidden; border-radius: 5px; background-color: white;">
                    <div class="marquee-content" style="animation: marquee 30s linear infinite; padding: 10px;">
                        {marquee_content}
                    </div>
                </div>
                <style>
                    @keyframes marquee {{
                        0%   {{ transform: translateY(0); }}
                        100% {{ transform: translateY(-50%); }}
                    }}
                    .marquee-content:hover {{
                        animation-play-state: paused;
                    }}
                </style>
            """
            st.sidebar.markdown(marquee_html, unsafe_allow_html=True)
        else:
            st.sidebar.info("No recent events found in the last 5 days.")

        # Main content
        st.title("Global Disaster News Feed")

        # Filter data by date
        filtered_df = df[
            (df['timestamp'] >= start_date_utc) &
            (df['timestamp'] <= end_date_utc)
        ]
        
        # Filter by selected disaster types
        if selected_disaster_types:
            filtered_df = filtered_df[filtered_df['disaster_event'].isin(selected_disaster_types)]
            if filtered_df.empty:
                st.info(f"No disaster events found for the selected types: {', '.join(selected_disaster_types)}")

        # Download button
        if not filtered_df.empty:
            csv = filtered_df[['title', 'disaster_event', 'timestamp', 'source', 'url', 'Location']].to_csv(index=False)
            st.download_button(
                "Download Data as CSV",
                csv,
                "disaster_data.csv",
                "text/csv"
            )

        # News feed with pagination
        if 'news_count' not in st.session_state:
            st.session_state.news_count = 20

        # Display news items with improved styling
        for _, row in filtered_df.head(st.session_state.news_count).iterrows():
            with st.container():
                st.markdown(f"""
                    <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #f9f9f9; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <div style="min-width: 80px; text-align: center; background-color: {row['color']}; color: white; padding: 8px; border-radius: 5px;">
                                <strong>{row['disaster_event']}</strong>
                            </div>
                            <div style="flex-grow: 1;">
                                <h4 style="color: #333; margin: 0 0 10px 0;">{row['title']}</h4>
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

        if st.button("Load More"):
            st.session_state.news_count += 20

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()