#!/usr/bin/env python3
import os
import json
import sys
from openai import OpenAI

def test_openrouter_api(api_key, json_path, query):
    """
    Test the OpenRouter API call with the DeepSeekR1Free model
    
    Args:
        api_key: OpenRouter API key
        json_path: Path to the anime JSON file
        query: User query for anime recommendations
    """
    # Load anime data
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            anime_data = json.load(f)
        print(f"Successfully loaded {len(anime_data)} anime entries from {json_path}")
    except Exception as e:
        print(f"Error loading anime data: {e}")
        return
    
    # Format anime data as context
    context = "Here is information about anime from the Winter 2025 season:\n\n"
    
    # Limit to first 15 anime to avoid token limits
    for i, anime in enumerate(anime_data[:15], 1):
        title = anime.get('title', 'Unknown Title')
        synopsis = anime.get('synopsis', 'No synopsis available')
        # Truncate synopsis if too long
        if len(synopsis) > 200:
            synopsis = synopsis[:200] + "..."
        context += f"{i}. {title}\nSynopsis: {synopsis}\n\n"
    
    # Create the prompt
    prompt = f"""You are an anime recommendation assistant. I'll provide you with information about anime from the Winter 2025 season.

{context}

User Query: {query}

Please provide anime recommendations based on the user's query. PRIORITIZE recommending anime from the Winter 2025 list I provided above.

However, you can also recommend anime from your general knowledge if:
1. There are no good matches in the Winter 2025 list, or
2. You want to provide additional context by comparing with well-known anime.

For each recommendation, explain why it might be a good match for the user. Clearly indicate which recommendations are from the Winter 2025 season and which are from your general knowledge.
"""
    
    print("\n--- Sending the following prompt to OpenRouter API ---")
    print(f"Prompt length: {len(prompt)} characters")
    print("First 200 characters of prompt:", prompt[:200], "...")
    print("Last 200 characters of prompt:", prompt[-200:], "...")
    
    try:
        # Initialize OpenAI client with OpenRouter base URL
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # Call the OpenRouter API
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",  # DeepSeekR1Free model
            messages=[
                {"role": "system", "content": "You are an anime recommendation assistant with knowledge of anime across all seasons. You prioritize recommending anime from the current season when appropriate, but can also suggest anime from other seasons when relevant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        print("\n--- API Response ---")
        print(f"Response model: {response.model}")
        print(f"Response tokens: {response.usage.completion_tokens} completion, {response.usage.prompt_tokens} prompt, {response.usage.total_tokens} total")
        print("\nResponse content:")
        print(response.choices[0].message.content)
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"\nError calling OpenRouter API: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py YOUR_OPENROUTER_API_KEY [json_path] [query]")
        print("  - YOUR_OPENROUTER_API_KEY: Your OpenRouter API key")
        print("  - json_path: (Optional) Path to anime JSON file (default: most recent in data/)")
        print("  - query: (Optional) Query for anime recommendations (default: 'I like action anime with good fight scenes')")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Find the most recent JSON file if not provided
    if len(sys.argv) >= 3:
        json_path = sys.argv[2]
    else:
        import glob
        from os.path import getctime
        json_files = glob.glob("data/winter_2025_anime_*.json")
        if not json_files:
            print("No anime JSON files found in data/ directory. Please run scrape_anime.py first.")
            sys.exit(1)
        json_path = max(json_files, key=getctime)
        print(f"Using most recent JSON file: {json_path}")
    
    # Use default query if not provided
    query = sys.argv[3] if len(sys.argv) >= 4 else "I enjoyed 'The Angel Next Door Spoils Me Rotten'. What similar romance anime is available this season?"
    
    # Test the API
    test_openrouter_api(api_key, json_path, query) 