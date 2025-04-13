import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Display safety protocols for disaster prevention."""
    try:
        # Simple header with minimal styling
        st.title("Safety Protocols for Disaster Prevention")
        st.markdown("Learn how to prepare and stay safe during different types of disasters")
        
        # Search functionality
        search_query = st.text_input("Search for a specific disaster type", "", key="disaster_search")
        
        # Define disaster categories
        disaster_categories = {
            "Natural Disasters": ["Earthquake", "Flood", "Hurricane", "Tornado", "Tsunami", "Volcano"],
            "Weather Events": ["Blizzard", "Cyclone", "Heatwave", "Drought"],
            "Geological Events": ["Avalanche", "Landslide"]
        }
        
        # Create tabs for different categories
        tabs = st.tabs(list(disaster_categories.keys()))
        
        # Disaster data
        disaster_data = {
            "Avalanche": """
            - Avoid areas prone to avalanches during times of high risk.
            - Carry avalanche safety gear such as transceivers, probes, and shovels.
            - Travel in groups and keep an eye on each other.
            - Be aware of warning signs like recent snowfall, wind-loading, and terrain features.
            """,
            "Heatwave": """
            - Stay hydrated and avoid prolonged exposure to the sun.
            - Use fans or air conditioning to stay cool.
            - Check on vulnerable individuals like the elderly and young children.
            - Dress in lightweight, light-colored clothing.
            """,
            "Flood": """
            - Evacuate to higher ground if necessary.
            - Avoid walking or driving through floodwaters.
            - Turn off utilities if instructed to do so.
            - Have an emergency flood kit ready with essential items.
            """,
            "Hurricane": """
            - Follow evacuation orders from local authorities.
            - Board up windows and secure outdoor items.
            - Stay indoors during the storm.
            - Have a communication plan in place with family and friends.
            """,
            "Landslide": """
            - Avoid areas susceptible to landslides during heavy rainfall.
            - Monitor for signs of land movement like cracks or unusual noises.
            - Evacuate if instructed by authorities.
            - Have an emergency plan and supplies ready.
            """,
            "Blizzard": """
            - Stay indoors and avoid unnecessary travel.
            - Keep emergency supplies stocked, including food, water, and blankets.
            - Dress warmly in layers if you must go outside.
            - Watch for signs of frostbite and hypothermia.
            """,
            "Cyclone": """
            - Evacuate if advised by local authorities.
            - Secure loose objects and reinforce windows and doors.
            - Stay indoors during the storm.
            - Listen to weather updates from reliable sources.
            """,
            "Tsunami": """
            - Evacuate immediately if you are in a tsunami evacuation zone.
            - Move inland or to higher ground.
            - Stay away from the coast and low-lying areas.
            - Listen to emergency alerts and follow instructions.
            """,
            "Volcano": """
            - Follow evacuation orders from authorities if in an affected area.
            - Protect yourself from ashfall by staying indoors with windows and doors closed.
            - Wear masks to protect against volcanic ash inhalation.
            - Monitor volcanic activity updates from official sources.
            """,
            "Earthquake": """
            - Drop, cover, and hold on during shaking.
            - Move away from windows and heavy objects.
            - Have an emergency kit with supplies like water, food, and first aid.
            - Identify safe spots in each room of your home.
            """,
            "Drought": """
            - Conserve water by fixing leaks and reducing usage.
            - Avoid outdoor burning and adhere to water restrictions.
            - Plant drought-resistant crops and trees.
            - Monitor water sources and report any issues promptly.
            """,
            "Tornado": """
            - Seek shelter in a sturdy building or underground.
            - Stay away from windows and doors.
            - If outdoors, find a low-lying area and lie flat, covering your head.
            - Have a tornado emergency plan for your household.
            """
        }
        
        # Display disasters in tabs
        for i, (category, disasters) in enumerate(disaster_categories.items()):
            with tabs[i]:
                # Filter disasters based on search query
                filtered_disasters = [d for d in disasters if search_query.lower() in d.lower()]
                
                if not filtered_disasters:
                    st.info(f"No disasters found matching '{search_query}' in {category}.")
                else:
                    # Display each disaster in a simple container
                    for disaster in filtered_disasters:
                        if disaster in disaster_data:
                            with st.container():
                                st.subheader(disaster)
                                st.markdown(disaster_data[disaster])
                                st.divider()
        
        logger.info("Precaution page displayed successfully")
    except Exception as e:
        logger.error(f"Error displaying precaution page: {str(e)}")
        st.error("An error occurred while loading the precaution page. Please try again later.")

if __name__ == "__main__":
    main()