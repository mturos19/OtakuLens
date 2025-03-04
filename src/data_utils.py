import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

def scrape_livechart_winter_2025():
    """
    Scrapes anime titles and synopsis for Winter 2025 season from livechart.me
    Returns a JSON-formatted string of the data and also saves it to a file
    """
    # URL for Winter 2025 season on livechart.me
    url = "https://www.livechart.me/winter-2025/tv"
    
    # Set a user agent to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all anime entries
        anime_entries = soup.select('.anime-card')
        
        anime_data = []
        
        for entry in anime_entries:
            try:
                # Extract title
                title_element = entry.select_one('.main-title')
                title = title_element.text.strip() if title_element else "Unknown Title"
                
                # Extract synopsis
                synopsis_element = entry.select_one('.anime-synopsis')
                synopsis = synopsis_element.text.strip() if synopsis_element else "No synopsis available"
                
                # Extract image URL if available
                image_element = entry.select_one('.poster-container img')
                image_url = image_element['src'] if image_element and 'src' in image_element.attrs else None
                
                # Extract additional info if needed
                anime_info = {
                    "title": title,
                    "synopsis": synopsis,
                    "image_url": image_url,
                    "season": "Winter 2025"
                }
                
                anime_data.append(anime_info)
                
                # Add a small delay to be respectful to the server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing an entry: {e}")
                continue
        
        # Create output directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Save data to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/winter_2025_anime_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(anime_data, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully scraped {len(anime_data)} anime entries. Data saved to {filename}")
        
        return anime_data
        
    except Exception as e:
        print(f"Error scraping data: {e}")
        return []

def save_anime_data_to_json(data, filename=None):
    """
    Saves anime data to a JSON file
    
    Args:
        data: List of dictionaries containing anime information
        filename: Optional custom filename, otherwise generates one with timestamp
    
    Returns:
        Path to the saved file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/anime_data_{timestamp}.json"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {filename}")
    return filename

