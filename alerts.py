import streamlit as st
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import pandas as pd
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

def send_email(email):
    """Send confirmation email to subscriber with error handling."""
    try:
        email_sender = os.getenv('EMAIL_SENDER')
        email_password = os.getenv('EMAIL_PASSWORD')
        if not email_sender or not email_password:
            raise ValueError("Email credentials not found in environment variables")

        email_receiver = email
        subject = "Subscription Confirmation"

        # Create a message with HTML content
        msg = MIMEMultipart('alternative')
        msg['From'] = email_sender
        msg['To'] = email
        msg['Subject'] = subject

        # Plain text version (optional)
        text_part = MIMEText("Plain text version of the email", 'plain')
        msg.attach(text_part)
        
        # HTML version with bold formatting and larger headings
        html_part = MIMEText(f"""
        <html>
        <head>
            <style>
                h2 {{
                    font-size: 20px;
                    font-weight: bold;
                }}
                p, li {{
                    font-size: 16px;
                }}
            </style>
        </head>
        <body>
        <p>Congratulations! You are now successfully subscribed to Geospatial Visualization for Disaster Monitoring. Thank you for choosing to stay informed and prepared in times of crisis.</p>
        <p>As a subscriber, you will receive timely updates and alerts regarding disasters and emergencies around the world based on your preferences. Our system utilizes advanced geospatial technology to provide you with accurate and up-to-date information, helping you make informed decisions to ensure your safety and well-being.</p>
        <p>Here's what you can expect from your subscription:</p>
        <ol>
            <li><strong>Real-time Alerts:</strong> Instant notifications about ongoing disasters, emergencies, and significant events worldwide.</li>
            <li><strong>Geospatial Visualization:</strong> Interactive maps and visualizations to track disaster events and their impact in real-time.</li>
            <li><strong>Customizable Preferences:</strong> Tailor your subscription preferences to receive alerts specific to your location, areas of interest, and types of disasters.</li>
        </ol>
        <p>Stay tuned for your first update, and in the meantime, feel free to explore the our platform and its features.</p>
        <p>Thank you for joining us in our mission to enhance disaster preparedness and response through innovative geospatial technology.</p>
        <p>Best regards,<br>The Geo-Spatial Visualization for Disaster Monitoring Team</p>
        </body>
        </html>
        """, 'html')
        msg.attach(html_part)

        # Set Content-Type header for HTML rendering
        msg['Content-Type'] = "text/html"

        # Add SSL (layer of security)
        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, msg.as_string())
        
        logger.info(f"Confirmation email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        st.error("Failed to send confirmation email. Please try again later.")
        return False

def main():
    try:
        # Initialize session state if not already done
        if 'username' not in st.session_state:
            st.session_state.username = ''
        
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
        st.title("Geospatial Visualization for Disaster Monitoring")
        selected_events = st.multiselect(
            "Select Disaster Events", 
            ["All"] + list(df["disaster_event"].unique()), 
            default=["All"]
        )
        selected_location = st.multiselect(
            "Select Disaster Events Location", 
            list(df["Location"].unique())
        )

        # Date filtering
        start_date_min = datetime.utcnow().date() - timedelta(days=2)
        start_date_utc = datetime.combine(start_date_min, datetime.min.time()).replace(tzinfo=timezone.utc)

        # Filter dataframe
        if "All" in selected_events:
            filtered_df = df[(df['timestamp'] >= start_date_utc) & df['Location'].isin(selected_location)]
        else:
            filtered_df = df[
                (df['timestamp'] >= start_date_utc) & 
                df['Location'].isin(selected_location) & 
                (df['disaster_event'].isin(selected_events))
            ]

        # Subscription handling
        if st.button("Subscribe to Alerts"):
            if st.session_state.username == '':
                st.header(':red[Login Now to Get Custom Alerts]')
            elif not selected_events:
                st.error('Disaster Event is not Selected')
            elif selected_location == [None] or not selected_location:
                st.error('Location is not Selected')
            else:
                try:
                    subscriptions_db = client[os.getenv('MONGODB_DB', 'newsfetcher')]
                    subscriptions_collection = subscriptions_db["alerts"]
                    subscription_data = {
                        "email": st.session_state.useremail,
                        "selected_events": selected_events,
                        "selected_locations": selected_location,
                        "subscription_date": datetime.utcnow()
                    }
                    subscriptions_collection.insert_one(subscription_data)
                    st.success("Subscription successful! You will receive alerts.")
                    st.balloons()
                    
                    # Send confirmation email
                    if send_email(st.session_state.useremail):
                        logger.info(f"User {st.session_state.username} subscribed to alerts")
                except Exception as e:
                    logger.error(f"Error saving subscription: {str(e)}")
                    st.error("Failed to save subscription. Please try again later.")

        st.write("[Explore the GitHub Repository](https://github.com/Samar23dev/Disaster_Info)")

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()


