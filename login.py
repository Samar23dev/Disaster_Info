import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, exceptions
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

# Initialize Firebase
try:
    cred = credentials.Certificate("firebase-credentials.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")
    st.error("Failed to initialize authentication service. Please try again later.")

def send_email(email):
    """Send welcome email to new user with error handling."""
    try:
        email_sender = os.getenv('EMAIL_SENDER')
        email_password = os.getenv('EMAIL_PASSWORD')
        subject = "Welcome to Geo-Spatial Visualization for Disaster Monitoring"

        # Create a message with HTML content
        msg = MIMEMultipart('alternative')
        msg['From'] = email_sender
        msg['To'] = email
        msg['Subject'] = subject

        # HTML version of the email
        html_content = f"""
        <html>
        <body>
          <p>Dear User,</p>
          <p>Thank you for signing up for Geo-Spatial Visualization for Disaster Monitoring!</p>
          <h2>Key Features:</h2>
          <ol>
            <li><b>Interactive Map Visualization</b></li>
            <li><b>Advanced Filtering Options</b></li>
            <li><b>Insights and Analytics</b></li>
            <li><b>Key Events Marquee</b></li>
            <li><b>Dynamic Updates</b></li>
          </ol>
          <p>Explore our GitHub Repository for more details: <a href="https://github.com/Samar23dev/Disaster_Info">Link to GitHub</a></p>
          <p>Best regards,<br>The Geo-Spatial Visualization for Disaster Monitoring Team</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))

        # Send the email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email, msg.as_string())
        
        logger.info(f"Welcome email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        st.error("Failed to send welcome email. Please try again later.")
        return False

def notify_user(message, level='info'):
    """Helper function to notify user with Streamlit."""
    if level == 'success':
        st.success(message)
    elif level == 'error':
        st.error(message)
    else:
        st.info(message)

def main():
    try:
        st.title(':green[Welcome to Geospatial Visualization for Disaster Monitoring]')

        # Initialize session state variables
        if 'username' not in st.session_state:
            st.session_state.update({'username': '', 'useremail': '', 'signedout': False, 'signout': False})

        def login_user(email, password):
            """Handle user login with error handling."""
            try:
                user = auth.get_user_by_email(email)
                st.session_state.update({'username': user.uid, 'useremail': user.email, 'signedout': True, 'signout': True})
                notify_user("Login Successful", 'success')
                logger.info(f"User {email} logged in successfully")
            except exceptions.InvalidArgumentError:
                notify_user("Invalid email address. Please enter a valid email address.", 'error')
                logger.warning(f"Login attempt with invalid email: {email}")
            except Exception as e:
                notify_user("Login Failed. Please check your credentials.", 'error')
                logger.error(f"Login failed for {email}: {str(e)}")

        def signout_user():
            """Handle user signout."""
            st.session_state.update({'signout': False, 'signedout': False, 'username': '', 'useremail': ''})
            logger.info("User signed out")

        def create_user(email, password, username):
            """Handle user creation with error handling."""
            if len(password) < 6:
                notify_user("Password must be at least 6 characters long.", 'error')
                logger.warning(f"Account creation attempt with short password for {email}")
                return False
            
            try:
                # Check if the username already exists
                all_users = auth.list_users()
                if any(user.uid == username for user in all_users.users):
                    notify_user("Username already exists. Please choose a different username.", 'error')
                    logger.warning(f"Account creation attempt with existing username: {username}")
                    return False

                # Create user
                user = auth.create_user(email=email, password=password, uid=username)
                notify_user('Account created successfully! Login now to Explore...', 'success')
                st.balloons()
                
                # Send welcome email
                if send_email(email):
                    logger.info(f"New user account created: {email}")
                    return True
                return False
            except exceptions.InvalidArgumentError:
                notify_user("Invalid email address. Please enter a valid email address.", 'error')
                logger.warning(f"Account creation attempt with invalid email: {email}")
                return False
            except Exception as e:
                notify_user(f"Account creation failed: {str(e)}", 'error')
                logger.error(f"Account creation failed for {email}: {str(e)}")
                return False

        # Main UI logic
        with st.form("user_form"):
            choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])

            email = st.text_input('Email Address')
            password = st.text_input('Password', type='password')
            if choice == 'Sign Up':
                username = st.text_input('Username')
                submit_button = st.form_submit_button('Create my account', on_click=lambda: create_user(email, password, username))
            else:
                submit_button = st.form_submit_button('Login', on_click=lambda: login_user(email, password))

        if st.session_state.signout:
            st.text(f'Name: {st.session_state.username}')
            st.text(f'Email id: {st.session_state.useremail}')
            st.button('Sign out', on_click=signout_user)

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()

