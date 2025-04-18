import streamlit as st
import logging
import json
import pandas as pd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("precausion")

st.markdown("""
<style>
    .header {background-color: #0072B5; color: white; padding: 1rem; border-radius: 5px; text-align: center; margin-bottom: 1rem;}
    .contact-card {border-left: 3px solid #0072B5; padding: 10px; margin-bottom: 8px;}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<div class="header"><h1>🛡️ Emergency Operations Dashboard</h1><p>Quick access to emergency contact details and safety protocols across India</p></div>', unsafe_allow_html=True)
    
    try:
        # Load data
        with open("assets/emergency.json", "r") as f:
            data = json.load(f)
        
        centers = data.get("Emergency_Operations_Centers", [])
        df = pd.DataFrame(centers)
        
        # Sidebar filter
        st.sidebar.header("🔍 Filter")
        state = st.sidebar.selectbox("Select a State/Ministry", ["All"] + sorted(df["Ministry/State"].unique()))
        
        # Quick emergency numbers
        st.sidebar.header("🚨 Emergency Numbers")
        st.sidebar.info("**National Emergency:** 112\n\n**Ambulance:** 108\n\n**Fire:** 101\n\n**Women Helpline:** 181")
        
        # Filter data based on selection
        if state != "All":
            filtered_df = df[df["Ministry/State"] == state]
        else:
            filtered_df = df
        
        # Create tabs for better organization
        tab1, tab2 = st.tabs(["📞 Emergency Contacts", "🧰 Safety Protocols"])
        
        with tab1:
            st.subheader(f"Emergency Contact Directory {f'for {state}' if state != 'All' else ''}")
            
            # Display contacts in a simple card format
            cols = st.columns(3)
            for i, row in filtered_df.iterrows():
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="contact-card">
                        <h4>{row["Ministry/State"]}</h4>
                        <p><b>In charge:</b> {row["In charge"]}</p>
                        <p><b>Contact:</b> {row["Contact Number"]}</p>
                        <p><b>Email:</b> {row["Email"]}</p>
                        <p><b>Timings:</b> {row["Timings"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Also show as a table for easy reference
            with st.expander("View as Table"):
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        with tab2:
            st.subheader("Safety Protocols for Disaster Prevention")
            
            # Simplified disaster data
            disasters = {
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
        
            
            # Display protocols in columns
            col1, col2 = st.columns(2)
            
            for i, (disaster, protocol) in enumerate(disasters.items()):
                if i % 2 == 0:
                    with col1:
                        with st.expander(f"🔹 {disaster}"):
                            st.write(protocol)
                else:
                    with col2:
                        with st.expander(f"🔹 {disaster}"):
                            st.write(protocol)
        
        # Footer
        st.markdown("---")
        st.caption("For more information, visit the official National Disaster Management Authority website. In case of emergency, contact the appropriate authorities immediately.")
        
        logger.info("Dashboard displayed successfully")
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error(f"⚠️ Failed to load emergency data. Please check the data file.")

if __name__ == "__main__":
    main()