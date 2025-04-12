import streamlit as st
from streamlit_option_menu import option_menu
import logging
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config with custom theme
st.set_page_config(
    page_title="Disaster Information System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1E88E5;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.5rem;
        font-weight: 500;
        color: #424242;
        margin-bottom: 1.5rem;
    }
    
    /* Card styling */
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f0f2f6;
        padding: 1rem 0;
    }
    
    /* Remove unwanted white spaces */
    .block-container {
        padding-top: 0;
        padding-bottom: 0;
        margin-top: 0;
    }
    
    /* Fix sidebar spacing */
    section[data-testid="stSidebar"] > div {
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* Fix main content spacing */
    .main > div {
        padding-top: 0;
        padding-bottom: 0;
    }
    
    /* Fix navigation menu spacing */
    .stHorizontalBlock {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 0.5rem;
        font-weight: 500;
    }
    
    /* Selectbox styling */
    .stSelectbox>div>div>div {
        background-color: white;
        border-radius: 5px;
    }
    
    /* Date input styling */
    .stDateInput>div>div>div>input {
        background-color: white;
        border-radius: 5px;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1rem;
        background-color: #f0f2f6;
        border-top: 1px solid #e0e0e0;
        margin-top: 1rem;
    }
    
    /* Remove default streamlit padding */
    .css-18e3th9 {
        padding-top: 0;
        padding-bottom: 0;
    }
    
    .css-1d391kg {
        padding-top: 0;
        padding-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

def load_module(module_name):
    """Safely load and run a module's main function."""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'main'):
            module.main()
        else:
            st.error(f"Module {module_name} does not have a main function")
    except Exception as e:
        logger.error(f"Error loading module {module_name}: {str(e)}")
        st.error(f"Error loading {module_name}. Please try again later.")

def main():
    try:
        # Add a header with logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<h1 class="main-title">Disaster Information System</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle">Real-time monitoring and visualization of global disasters</p>', unsafe_allow_html=True)
        
        # Set up the navigation menu with improved styling
        selected = option_menu(
            menu_title=None,
            options=["Home", "Alerts", "Insight", "Weather", "About", "Precausion", "Login"],
            icons=["house", "bell", "globe", "cloud-sun", "info", "7-circle", "key"],
            orientation="horizontal",
            default_index=0,  # Set Home as default
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#1E88E5", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
                "nav-link-selected": {"background-color": "#1E88E5", "color": "white"},
            }
        )

        # Route to appropriate module
        module_map = {
            "Home": "home",
            "Alerts": "alerts",
            "Login": "login",
            "About": "about",
            "Insight": "insight",
            "Precausion": "precausion",
            "Weather": "weather"
        }

        if selected in module_map:
            load_module(module_map[selected])
        else:
            st.error("Invalid navigation selection")
            
        # Add a footer
        st.markdown("""
        <div class="footer">
            <p>© 2023 Disaster Information System | <a href="https://github.com/yourusername/disaster-info" target="_blank">GitHub</a></p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
