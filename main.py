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
        st.title("Disaster News Extractor and Geospatial Visualizer")
        
        # Set up the navigation menu with improved styling
        selected = option_menu(
            menu_title=None,
            options=["Home","Insight", "Alerts", "Weather", "About", "Precaution", "Login/SignUp"],
            icons=["house", "globe", "bell", "cloud-sun", "info", "7-circle", "key"],
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
            "Login/SignUp": "login",
            "About": "about",
            "Insight": "insight",
            "Precaution": "precaution",
            "Weather": "weather"
        }

        if selected in module_map:
            load_module(module_map[selected])
        else:
            st.error("Invalid navigation selection")
            
        # Add a footer
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background-color: #f0f2f6; border-top: 1px solid #e0e0e0; margin-top: 1rem;">
            <p>©Geospatial Visualizer and Disaster News Extractor | <a href="https://github.com/Samar23dev/Disaster_Info" target="_blank">GitHub</a></p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
