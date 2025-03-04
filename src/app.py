import os
import streamlit as st
import json
import glob
import traceback
from datetime import datetime
from llm_utils import AnimeRecommender
from data_utils import scrape_livechart_winter_2025

# Set page configuration
st.set_page_config(
    page_title="OtakuLens - Anime Recommender",
    page_icon="🎭",
    layout="wide"
)

# Initialize session state variables
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'recommender' not in st.session_state:
    st.session_state.recommender = None
if 'anime_data' not in st.session_state:
    st.session_state.anime_data = []
if 'json_path' not in st.session_state:
    st.session_state.json_path = ""
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = ""
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False
if 'api_debug_info' not in st.session_state:
    st.session_state.api_debug_info = {}

# Function to initialize the recommender
def initialize_recommender():
    try:
        st.session_state.recommender = AnimeRecommender(api_key=st.session_state.api_key)
        return True
    except Exception as e:
        st.error(f"Error initializing recommender: {e}")
        st.session_state.error_message = f"Error initializing recommender: {str(e)}\n{traceback.format_exc()}"
        return False

# Function to load anime data
def load_anime_data(json_path):
    if not st.session_state.recommender:
        st.error("Please set your OpenRouter API key first.")
        return False
    
    try:
        success = st.session_state.recommender.load_anime_data(json_path)
        if success:
            with open(json_path, 'r', encoding='utf-8') as f:
                st.session_state.anime_data = json.load(f)
            st.session_state.json_path = json_path
            return True
        else:
            st.error(f"Failed to load anime data from {json_path}")
            return False
    except Exception as e:
        st.error(f"Error loading anime data: {e}")
        st.session_state.error_message = f"Error loading anime data: {str(e)}\n{traceback.format_exc()}"
        return False

# Callback function for the recommendation button
def on_recommendation_button_click(query):
    st.session_state.show_recommendations = True
    get_recommendations(query)

# Function to get recommendations
def get_recommendations(query):
    if not st.session_state.recommender:
        st.error("Please set your OpenRouter API key first.")
        return
    
    if not st.session_state.anime_data:
        st.error("Please load anime data first.")
        return
    
    try:
        # Debug info
        st.session_state.error_message = f"Attempting to get recommendations with query: {query}"
        
        # Get recommendations with fewer entries to avoid token limits
        recommendations = st.session_state.recommender.get_recommendations(
            query, 
            max_entries=10,  # Reduced to ensure we're well within token limits
            max_tokens=1200   # Increased from 800 to get more complete responses
        )
        
        # Get debug info from the recommender
        st.session_state.api_debug_info = st.session_state.recommender.get_debug_info()
        
        # Debug info
        st.session_state.error_message += f"\nReceived response of length: {len(recommendations) if recommendations else 0}"
        
        # Store recommendations in session state
        st.session_state.recommendations = recommendations
        
    except Exception as e:
        error_details = f"Error getting recommendations: {str(e)}\n{traceback.format_exc()}"
        st.error("Error getting recommendations. See details in the Debug section.")
        st.session_state.error_message = error_details
        st.session_state.recommendations = f"Error: {str(e)}"

# Function to scrape new anime data
def scrape_new_data():
    try:
        with st.spinner("Scraping anime data from livechart.me..."):
            anime_data = scrape_livechart_winter_2025()
            if anime_data:
                st.success(f"Successfully scraped {len(anime_data)} anime entries.")
                # Get the latest JSON file
                json_files = glob.glob("data/winter_2025_anime_*.json")
                if json_files:
                    latest_file = max(json_files, key=os.path.getctime)
                    st.session_state.json_path = latest_file
                    load_anime_data(latest_file)
                return True
            else:
                st.error("Failed to scrape anime data.")
                return False
    except Exception as e:
        st.error(f"Error scraping data: {e}")
        st.session_state.error_message = f"Error scraping data: {str(e)}\n{traceback.format_exc()}"
        return False

# Main app layout
st.title("OtakuLens - Anime Recommender")
st.markdown("Get personalized anime recommendations from the Winter 2025 season!")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Key input
    api_key = st.text_input("OpenRouter API Key", 
                           value=st.session_state.api_key,
                           type="password",
                           help="Get your API key from https://openrouter.ai/")
    
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        if api_key:
            if initialize_recommender():
                st.success("API key set successfully!")
    
    st.divider()
    
    # Data management section
    st.subheader("Anime Data")
    
    # Option to scrape new data
    if st.button("Scrape New Anime Data"):
        scrape_new_data()
    
    # Option to select existing JSON file
    st.subheader("Or select existing data:")
    json_files = glob.glob("data/winter_2025_anime_*.json")
    if json_files:
        json_files.sort(reverse=True)  # Most recent first
        selected_file = st.selectbox(
            "Select JSON file",
            options=json_files,
            format_func=lambda x: f"{os.path.basename(x)} ({datetime.fromtimestamp(os.path.getctime(x)).strftime('%Y-%m-%d %H:%M')})"
        )
        
        if selected_file != st.session_state.json_path:
            if st.button("Load Selected Data"):
                load_anime_data(selected_file)
    else:
        st.info("No anime data files found. Please scrape new data.")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Get Recommendations")
    
    # Query input
    query = st.text_area(
        "What anime are you looking for?",
        placeholder="Example: I enjoyed 'The Angel Next Door Spoils Me Rotten'. What similar romance anime is available this season?",
        height=100
    )
    
    # Get recommendations button - using a direct function call
    if st.button(
        "Get Recommendations", 
        type="primary", 
        disabled=not (st.session_state.recommender and st.session_state.anime_data)
    ):
        st.session_state.show_recommendations = True
        get_recommendations(query)

with col2:
    st.header("Recommendations")
    
    # Display recommendations container
    recommendations_container = st.container()
    
    # Always display recommendations if they exist
    with recommendations_container:
        if st.session_state.recommendations:
            st.markdown(st.session_state.recommendations)
            
            # Check if the response appears to be truncated
            if len(st.session_state.recommendations) > 100 and not st.session_state.recommendations.endswith(('.', '!', '?', ')', ']', '}')):
                st.warning("⚠️ **Note:** The recommendations appear to be truncated due to token limits. Consider using a more specific query or reducing the scope of your request.")
            
            # Add a download button for the recommendations
            st.download_button(
                label="Download Recommendations",
                data=st.session_state.recommendations,
                file_name="anime_recommendations.txt",
                mime="text/plain"
            )
        else:
            st.info("Enter your query and click 'Get Recommendations' to see results.")

# Display loaded anime data
if st.session_state.anime_data:
    with st.expander("View Loaded Anime Data"):
        st.subheader(f"Loaded {len(st.session_state.anime_data)} anime entries from {os.path.basename(st.session_state.json_path)}")
        
        for i, anime in enumerate(st.session_state.anime_data[:20], 1):  # Limit to first 20 for performance
            st.markdown(f"**{i}. {anime.get('title', 'Unknown Title')}**")
            st.markdown(f"*{anime.get('synopsis', 'No synopsis available')[:200]}...*" if len(anime.get('synopsis', '')) > 200 else f"*{anime.get('synopsis', 'No synopsis available')}*")
            st.divider()

# Debug section - moved outside of sidebar to avoid nested expanders
st.header("Debug Information")
debug_tab1, debug_tab2, debug_tab3, debug_tab4 = st.tabs(["App State", "API Request", "API Response", "Error Log"])

with debug_tab1:
    if st.button("Print Current State"):
        state_info = "\n".join([
            f"API Key Set: {'Yes' if st.session_state.api_key else 'No'}",
            f"Recommender Initialized: {'Yes' if st.session_state.recommender else 'No'}",
            f"Anime Data Loaded: {'Yes (' + str(len(st.session_state.anime_data)) + ' entries)' if st.session_state.anime_data else 'No'}",
            f"JSON Path: {st.session_state.json_path}",
            f"Recommendations Length: {len(st.session_state.recommendations) if st.session_state.recommendations else 0}",
            f"Show Recommendations: {st.session_state.show_recommendations}"
        ])
        st.session_state.error_message += f"\n\nCurrent State:\n{state_info}"
    
    # Display current state
    st.write(f"API Key Set: {'Yes' if st.session_state.api_key else 'No'}")
    st.write(f"Recommender Initialized: {'Yes' if st.session_state.recommender else 'No'}")
    st.write(f"Anime Data Loaded: {'Yes (' + str(len(st.session_state.anime_data)) + ' entries)' if st.session_state.anime_data else 'No'}")
    st.write(f"JSON Path: {st.session_state.json_path}")
    st.write(f"Recommendations Length: {len(st.session_state.recommendations) if st.session_state.recommendations else 0}")
    st.write(f"Show Recommendations: {st.session_state.show_recommendations}")

with debug_tab2:
    # Last Request
    if st.session_state.api_debug_info.get('last_request'):
        req = st.session_state.api_debug_info['last_request']
        st.write(f"Model: {req.get('model')}")
        st.write(f"Temperature: {req.get('temperature')}")
        st.write(f"Max Tokens: {req.get('max_tokens')}")
        st.text_area("Prompt", value=req.get('prompt', ''), height=300)
    else:
        st.info("No API request information available yet.")

with debug_tab3:
    # Last Response
    if st.session_state.api_debug_info.get('last_response'):
        resp = st.session_state.api_debug_info['last_response']
        st.write(f"Model: {resp.get('model')}")
        if resp.get('usage'):
            st.write(f"Completion Tokens: {resp['usage'].get('completion_tokens')}")
            st.write(f"Prompt Tokens: {resp['usage'].get('prompt_tokens')}")
            st.write(f"Total Tokens: {resp['usage'].get('total_tokens')}")
        st.text_area("Content", value=resp.get('content', ''), height=300)
    else:
        st.info("No API response information available yet.")

with debug_tab4:
    # Last Error and Debug Log
    if st.session_state.api_debug_info.get('last_error'):
        st.error(st.session_state.api_debug_info['last_error'])
    
    st.text_area("Debug Log", value=st.session_state.error_message, height=300)
    if st.button("Clear Debug Log"):
        st.session_state.error_message = ""

# Footer
st.markdown("---")
st.markdown("OtakuLens - Powered by DeepSeekR1Free via OpenRouter") 