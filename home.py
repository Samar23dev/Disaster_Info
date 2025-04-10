import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
from wordcloud import WordCloud
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
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            st.error("Error processing data. Please try again later.")
            return

        # UI Components
        st.title("Geospatial Visualization for Disaster Monitoring")
        selected_events = st.multiselect(
            "Select Disaster Events",
            ["All"] + list(df["disaster_event"].unique()),
            default=["All"]
        )

        # Sidebar filters
        st.sidebar.header('Filter Data')
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

        # Date filtering
        start_date_utc = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_date_utc = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

        # Filter dataframe
        if "All" in selected_events:
            filtered_df = df[(df['timestamp'] >= start_date_utc) & (df['timestamp'] <= end_date_utc)]
        else:
            filtered_df = df[
                (df['timestamp'] >= start_date_utc) &
                (df['timestamp'] <= end_date_utc) &
                (df['disaster_event'].isin(selected_events))
            ]

        if filtered_df.empty:
            st.subheader(":green[No Disaster data available after filtering based on the condition]")
            return

        # Map creation
        map_center = (filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean())
        mymap = folium.Map(location=map_center, zoom_start=4, fullscreen_control=True)
        marker_cluster = MarkerCluster().add_to(mymap)

        # Add markers
        for index, row in filtered_df.iterrows():
            try:
                custom_icon_path = get_custom_icon_path(row['disaster_event'])
                custom_icon = folium.CustomIcon(
                    icon_image=custom_icon_path,
                    icon_size=(35, 35),
                    icon_anchor=(15, 30),
                    popup_anchor=(0, -25)
                )
                popup_content = f"<a href='{row['url']}' target='_blank'>{row['title']}</a>"
                tooltip_content = f"{row['disaster_event']}, {row['Location']}"
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=custom_icon,
                    tooltip=tooltip_content
                ).add_to(marker_cluster)
            except Exception as e:
                logger.error(f"Error adding marker for row {index}: {str(e)}")
                continue

        # Map styles
        base_map_styles = {
            'Terrain': 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            'Satellite': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            'OpenStreetMap': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'Stamen Terrain': 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg'
        }

        # Add base map styles
        for name, url in base_map_styles.items():
            folium.TileLayer(url, attr=f"© {name}", name=name).add_to(mymap)

        # Add layer control
        folium.LayerControl(collapsed=True).add_to(mymap)

        # Display map
        st_folium(mymap, width='100%', height=620)

        # Display filtered data
        with st.expander("Disaster Data Overview"):
            expander_title = f"### Disaster Data for {'All Events' if 'All' in selected_events else ', '.join(selected_events)}"
            st.markdown(expander_title, unsafe_allow_html=True)
            columns_to_display = ['title', 'disaster_event', 'timestamp', 'source', 'url', 'Location']
            st.write(filtered_df[columns_to_display])

        # Recent events marquee
        df_filtered = df[df['disaster_event'].isin(["Earthquake", "Flood", "Cyclone", "Volcano"])]
        seven_days_ago = pd.Timestamp(datetime.utcnow() - timedelta(days=5), tz="UTC")
        filtered_recent_events = df_filtered[df_filtered['timestamp'] >= seven_days_ago]
        filtered_recent_events_sorted = filtered_recent_events.sort_values(by='timestamp', ascending=False)

        # Create marquee content
        marquee_content = ""
        for index, row in filtered_recent_events_sorted.iterrows():
            marquee_content += f"<a href='{row['url']}' target='_blank'>{row['title']}</a> <br><br>"

        # Marquee HTML
        marquee_html = f"""
            <h1>Key Events</h1>
            <div class="marquee-container" onmouseover="stopMarquee()" onmouseout="startMarquee()">
                <div class="marquee-content">{marquee_content}</div>
            </div>
            <style>
                .marquee-container {{
                    height: 100%;
                    overflow: hidden;
                }}
                .marquee-content {{
                    animation: marquee 40s linear infinite;
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

        # Display marquee
        st.sidebar.markdown(marquee_html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
