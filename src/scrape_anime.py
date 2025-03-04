#!/usr/bin/env python3
from data_utils import scrape_livechart_winter_2025

if __name__ == "__main__":
    print("Starting to scrape Winter 2025 anime data from livechart.me...")
    anime_data = scrape_livechart_winter_2025()
    print(f"Scraped {len(anime_data)} anime entries.")
    
    # Print the first few entries as a preview
    if anime_data:
        print("\nPreview of the first 3 entries:")
        for i, anime in enumerate(anime_data[:3], 1):
            print(f"\n{i}. {anime['title']}")
            print(f"Synopsis: {anime['synopsis'][:100]}..." if len(anime['synopsis']) > 100 else f"Synopsis: {anime['synopsis']}") 