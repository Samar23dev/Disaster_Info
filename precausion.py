import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Display safety protocols for disaster prevention."""
    try:
        st.header("Safety Protocols for Disaster Prevention")

        # Use columns for layout
        col1, col2, col3 = st.columns(3)

        # Define a function to create an expander for each disaster type
        def create_expander(title, content, image_url=None):
            with st.expander(title, expanded=False):
                # Load the corresponding icon based on the title
                icon_path = f"icons/{title.lower()}.png"  # Assuming icons are named in lowercase
                st.image(icon_path, width=50)  # Display the icon with a specified width
                if image_url:
                    st.image(image_url, use_container_width=True)  # Display the main image
                st.markdown(content)

        # Disaster protocols in expanders with images
        create_expander("Avalanche", """
        - Avoid areas prone to avalanches during times of high risk.
        - Carry avalanche safety gear such as transceivers, probes, and shovels.
        - Travel in groups and keep an eye on each other.
        - Be aware of warning signs like recent snowfall, wind-loading, and terrain features.
        """, "https://example.com/avalanche_image.jpg")  # Replace with actual image URL

        create_expander("Heatwave", """
        - Stay hydrated and avoid prolonged exposure to the sun.
        - Use fans or air conditioning to stay cool.
        - Check on vulnerable individuals like the elderly and young children.
        - Dress in lightweight, light-colored clothing.
        """, "https://example.com/heatwave_image.jpg")  # Replace with actual image URL

        create_expander("Flood", """
        - Evacuate to higher ground if necessary.
        - Avoid walking or driving through floodwaters.
        - Turn off utilities if instructed to do so.
        - Have an emergency flood kit ready with essential items.
        """, "https://example.com/flood_image.jpg")  # Replace with actual image URL

        create_expander("Hurricane", """
        - Follow evacuation orders from local authorities.
        - Board up windows and secure outdoor items.
        - Stay indoors during the storm.
        - Have a communication plan in place with family and friends.
        """, "https://example.com/hurricane_image.jpg")  # Replace with actual image URL

        create_expander("Landslide", """
        - Avoid areas susceptible to landslides during heavy rainfall.
        - Monitor for signs of land movement like cracks or unusual noises.
        - Evacuate if instructed by authorities.
        - Have an emergency plan and supplies ready.
        """, "https://example.com/landslide_image.jpg")  # Replace with actual image URL

        create_expander("Blizzard", """
        - Stay indoors and avoid unnecessary travel.
        - Keep emergency supplies stocked, including food, water, and blankets.
        - Dress warmly in layers if you must go outside.
        - Watch for signs of frostbite and hypothermia.
        """, "https://example.com/blizzard_image.jpg")  # Replace with actual image URL

        create_expander("Cyclone", """
        - Evacuate if advised by local authorities.
        - Secure loose objects and reinforce windows and doors.
        - Stay indoors during the storm.
        - Listen to weather updates from reliable sources.
        """, "https://example.com/cyclone_image.jpg")  # Replace with actual image URL

        create_expander("Tsunami", """
        - Evacuate immediately if you are in a tsunami evacuation zone.
        - Move inland or to higher ground.
        - Stay away from the coast and low-lying areas.
        - Listen to emergency alerts and follow instructions.
        """, "https://example.com/tsunami_image.jpg")  # Replace with actual image URL

        create_expander("Volcano", """
        - Follow evacuation orders from authorities if in an affected area.
        - Protect yourself from ashfall by staying indoors with windows and doors closed.
        - Wear masks to protect against volcanic ash inhalation.
        - Monitor volcanic activity updates from official sources.
        """, "https://example.com/volcano_image.jpg")  # Replace with actual image URL

        create_expander("Earthquake", """
        - Drop, cover, and hold on during shaking.
        - Move away from windows and heavy objects.
        - Have an emergency kit with supplies like water, food, and first aid.
        - Identify safe spots in each room of your home.
        """, "https://example.com/earthquake_image.jpg")  # Replace with actual image URL

        create_expander("Drought", """
        - Conserve water by fixing leaks and reducing usage.
        - Avoid outdoor burning and adhere to water restrictions.
        - Plant drought-resistant crops and trees.
        - Monitor water sources and report any issues promptly.
        """, "https://example.com/drought_image.jpg")  # Replace with actual image URL

        create_expander("Tornado", """
        - Seek shelter in a sturdy building or underground.
        - Stay away from windows and doors.
        - If outdoors, find a low-lying area and lie flat, covering your head.
        - Have a tornado emergency plan for your household.
        """, "https://example.com/tornado_image.jpg")  # Replace with actual image URL

        logger.info("Precaution page displayed successfully")
    except Exception as e:
        logger.error(f"Error displaying precaution page: {str(e)}")
        st.error("An error occurred while loading the precaution page. Please try again later.")

if __name__ == "__main__":
    main()