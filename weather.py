import streamlit as st
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    try:
        # Add a header with improved styling
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #1E88E5; margin-bottom: 1rem;">Weather Monitoring</h2>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Real-time weather data and forecasts</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Get Windy API key
        windy_api_key = os.getenv('WINDY_API_KEY')
        if not windy_api_key:
            st.error("Windy API key not found. Please check your environment variables.")
            return

        # Create two columns for layout
        col1, col2 = st.columns([3, 1])

        with col1:
            # Windy map container
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #1E88E5; margin-bottom: 1rem;">Global Weather Map</h3>', unsafe_allow_html=True)
            
            # Windy map iframe with simplified controls
            windy_html = f"""
            <div style="width: 100%; height: 600px; border-radius: 10px; overflow: hidden;">
                <iframe
                    width="100%"
                    height="100%"
                    frameborder="0"
                    src="https://embed.windy.com/embed2.html?lat=20.593684&lon=78.962880&zoom=5&level=surface&overlay=wind&product=ecmwf&menu=&message=true&marker=&calendar=now&pressure=&type=satellite&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1&overlay=rain&overlay=wind&overlay=temp&overlay=clouds&overlay=pressure&overlay=waves"
                    style="border-radius: 10px;"
                ></iframe>
            </div>
            """
            st.markdown(windy_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # Weather alerts section
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #1E88E5; margin-bottom: 1rem;">Weather Alerts</h3>', unsafe_allow_html=True)
            
            alerts = [
                {"type": "Storm", "location": "Pacific Ocean", "severity": "High"},
                {"type": "Heatwave", "location": "South Asia", "severity": "Medium"},
                {"type": "Flood", "location": "Southeast Asia", "severity": "High"}
            ]
            
            for alert in alerts:
                severity_color = "#FF4500" if alert["severity"] == "High" else "#FFA500"
                st.markdown(f"""
                    <div style="padding: 10px; margin-bottom: 10px; border-left: 4px solid {severity_color}; background-color: #f8f9fa;">
                        <strong>{alert["type"]}</strong><br>
                        Location: {alert["location"]}<br>
                        Severity: <span style="color: {severity_color};">{alert["severity"]}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Weather data analysis section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #1E88E5; margin-bottom: 1rem;">Weather Data Analysis</h3>', unsafe_allow_html=True)
        
        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Storms", "3", "+1")
            
        with col2:
            st.metric("Temperature Anomalies", "5", "-2")
            
        with col3:
            st.metric("Precipitation Alerts", "2", "0")
        
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error in weather page: {str(e)}")
        st.error("An error occurred while loading the weather data. Please try again later.")

if __name__ == "__main__":
    main()
