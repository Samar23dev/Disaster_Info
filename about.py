import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Display information about the application."""
    try:
        st.title("Disaster Information System")
        st.markdown("""
        Welcome to the **Disaster Information System**! This web application monitors, visualizes, and provides insights on global disaster events in real-time. 
        By analyzing news articles from various sources, we extract valuable information about ongoing and past disasters, presenting it through an intuitive and interactive interface.
        """)

        st.subheader("Features")
        st.markdown("""
        - **Global Disaster News Feed**: Real-time news feed with color-coded disaster types and filtering options
        - **Interactive Map Visualization**: Geographic distribution of disaster events with detailed information
        - **Insights and Analytics**: Data visualization including charts, word clouds, and time series analysis
        - **Weather Monitoring**: Real-time weather data and forecasts for disaster-prone areas
        - **Alert System**: Subscription-based notifications for specific disaster types and locations
        - **Safety Protocols**: Comprehensive guidelines for different disaster types
        - **User Authentication**: Secure login and personalized experience
        """)

        st.subheader("Data Sources")
        st.markdown("""
        The project collects data from **NewsAPI**, providing access to various news articles. After preprocessing, the data is stored in **MongoDB**. 
        Weather data is sourced from the **Windy API**, offering real-time meteorological information. Additional data sources may be integrated to enhance coverage and accuracy.
        """)

        st.subheader("Technical Architecture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Frontend**")
            st.markdown("""
            - Streamlit: Web application framework
            - Folium: Interactive map visualization
            - Plotly: Interactive charts and visualizations
            - Matplotlib: Data visualization and word cloud generation
            """)
            
        with col2:
            st.markdown("**Backend**")
            st.markdown("""
            - Python: Core programming language
            - MongoDB: Database for storing disaster data
            - Pandas: Data manipulation and analysis
            - PyMongo: MongoDB connection and query handling
            - SMTP: Email notification system
            """)

        st.subheader("Project Structure")
        st.markdown("""
        - `main.py`: Application entry point and navigation
        - `home.py`: Global disaster news feed
        - `insight.py`: Data visualization and analytics
        - `weather.py`: Weather monitoring and alerts
        - `alerts.py`: Alert subscription system
        - `precausion.py`: Safety protocols and guidelines
        - `about.py`: Project information and documentation
        - `login.py`: User authentication system
        """)

        st.subheader("Contributors")
        st.markdown("""
        This project was developed by **Samar Mittal** and **Anay Mahajan**. We collaborated to create a comprehensive tool for monitoring and visualizing disaster events.
        """)

        st.subheader("GitHub Repository")
        st.markdown("[Explore the GitHub Repository](https://github.com/Samar23dev/Disaster_Info)")

        logger.info("About page displayed successfully")
    except Exception as e:
        logger.error(f"Error displaying about page: {str(e)}")
        st.error("An error occurred while loading the about page. Please try again later.")

if __name__ == "__main__":
    main()



