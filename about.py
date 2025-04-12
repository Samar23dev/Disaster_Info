import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Display information about the application."""
    try:
        st.title("🌍 Geo-Spatial Visualization for Disaster Monitoring")
        st.write(
            """
            Welcome to the **Geo-Spatial Visualization for Disaster Monitoring** application! This web application allows you to monitor and visualize disasters in real-time through the analysis of news articles. By extracting valuable information from various news sources, we aim to provide a comprehensive overview of ongoing and past disaster events.
            """
        )

        st.subheader("✨ Features")
        st.markdown("""
        - **Interactive Map Visualization**: View the geographical distribution of disaster events on an interactive map powered by Folium.
        - **Filtering Options**: Filter disaster events based on event type and date range using intuitive sidebar widgets.
        - **Insights and Analytics**: Gain insights into disaster events through various interactive visualizations, including charts, word clouds, and event counts over time.
        - **Key Events Marquee**: Stay updated with a scrolling marquee in the sidebar showcasing recent key events with clickable links for more information.
        - **Dynamic Updates**: The application dynamically updates visualizations and data based on user-selected filters.
        """)

        st.subheader("📊 Data Sources")
        st.write(
            """
            The project primarily collects data from **NewsAPI**, a service providing access to various news articles. After preprocessing, the data is stored in **MongoDB** with the database name **GeoNews**. Additional data sources may be integrated to enhance the coverage and accuracy of the information.
            """
        )

        st.subheader("🛠️ Technologies Used")
        st.markdown("""
        - **Python**: The programming language used for data processing and visualization.
        - **Streamlit**: The framework for building interactive web applications.
        - **Pandas**: A library for data manipulation and analysis.
        - **Folium**: A library for creating interactive maps.
        - **Plotly**: A library for generating interactive plots and charts.
        - **MongoDB**: The database for storing and querying geospatial data.
        """)

        st.subheader("👥 Contributors")
        st.write(
            """
            This project was developed by **Samar Mittal** and **Anay Mahajan**. We collaborated to create a comprehensive tool for monitoring and visualizing disaster events.
            """)

        st.subheader("🔗 GitHub Repository")
        st.write("[Explore the GitHub Repository](https://github.com/Samar23dev/Disaster_Info)")

        logger.info("About page displayed successfully")
    except Exception as e:
        logger.error(f"Error displaying about page: {str(e)}")
        st.error("An error occurred while loading the about page. Please try again later.")

if __name__ == "__main__":
    main()



