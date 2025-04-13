# Disaster Information System

## Overview
The Disaster Information System is a comprehensive web application that monitors, visualizes, and provides insights on global disaster events in real-time. By analyzing news articles from various sources, the system extracts valuable information about ongoing and past disasters, presenting it through an intuitive and interactive interface.

## Features

### 1. Global Disaster News Feed
- Real-time news feed of disaster events worldwide
- Color-coded disaster types for easy identification
- Filterable by date range and disaster type
- Interactive "Read More" links to original news sources
- Pagination with "Load More" functionality

### 2. Interactive Map Visualization
- Geographic distribution of disaster events
- Marker clustering for dense areas
- Popup information with disaster details
- Fullscreen mode for better exploration
- Customizable map layers

### 3. Insights and Analytics
- Disaster event distribution charts
- Location-based analysis
- Time series analysis of disaster frequency
- Word cloud visualization of disaster titles
- Interactive data tables

### 4. Weather Monitoring
- Real-time weather data visualization
- Global weather map with multiple overlays
- Weather alerts for severe conditions
- Temperature, precipitation, and wind data
- Customizable weather parameters

### 5. Alert System
- Subscription-based alert notifications
- Customizable alert preferences by disaster type and location
- Email confirmation for new subscribers
- Real-time updates on significant events

### 6. Safety Protocols
- Comprehensive safety guidelines for different disaster types
- Expandable sections for each disaster category
- Visual aids and instructions
- Emergency preparedness recommendations

### 7. User Authentication
- Secure login and registration system
- Personalized user experience
- Saved preferences and alert settings

## Technical Architecture

### Frontend
- **Streamlit**: Web application framework for creating interactive dashboards
- **Folium**: Interactive map visualization
- **Plotly**: Interactive charts and visualizations
- **Matplotlib**: Data visualization and word cloud generation
- **Custom CSS**: Enhanced styling and user interface

### Backend
- **Python**: Core programming language
- **MongoDB**: Database for storing disaster data and user information
- **Pandas**: Data manipulation and analysis
- **PyMongo**: MongoDB connection and query handling
- **SMTP**: Email notification system

### Data Sources
- News articles from various sources
- Weather data from Windy API
- Geospatial data for mapping

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Samar23dev/Disaster_Info.git
   cd Disaster_Info
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   MONGODB_URI=your_mongodb_connection_string
   MONGODB_DB=your_database_name
   MONGODB_COLLECTION=your_collection_name
   WINDY_API_KEY=your_windy_api_key
   EMAIL_SENDER=your_email_address
   EMAIL_PASSWORD=your_email_password
   ```

4. Run the application:
   ```
   streamlit run main.py
   ```

## Project Structure
- `main.py`: Application entry point and navigation
- `home.py`: Global disaster news feed
- `insight.py`: Data visualization and analytics
- `weather.py`: Weather monitoring and alerts
- `alerts.py`: Alert subscription system
- `precausion.py`: Safety protocols and guidelines
- `about.py`: Project information and documentation
- `login.py`: User authentication system

## Contributors
- **Samar Mittal**: Developer
- **Anay Mahajan**: Co-developer

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- NewsAPI for providing news data
- Windy API for weather information
- MongoDB for database services
- Streamlit for the web application framework
