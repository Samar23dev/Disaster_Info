import streamlit as st
from streamlit_option_menu import option_menu
import logging
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Disaster Information System",
    page_icon="🌍",
    layout="wide"
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
        # Set up the navigation menu
        selected = option_menu(
            menu_title="Disaster Information System",
            options=["Home", "Alerts", "Insight", "About", "Precausion", "Login"],
            icons=["house", "bell", "globe", "info", "7-circle", "key"],
            orientation="horizontal",
            default_index=0  # Set Home as default
        )

        # Route to appropriate module
        module_map = {
            "Home": "home",
            "Alerts": "alerts",
            "Login": "login",
            "About": "about",
            "Insight": "insight",
            "Precausion": "precausion"
        }

        if selected in module_map:
            load_module(module_map[selected])
        else:
            st.error("Invalid navigation selection")

    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
