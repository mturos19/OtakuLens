import os
import json
import requests
import time
from openai import OpenAI

class AnimeRecommender:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass it to the constructor.")
        
        # Initialize OpenAI client with OpenRouter base URL
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # Model ID for DeepSeekR1Free
        self.model_id = "deepseek/deepseek-r1:free"
        
        # Load anime data
        self.anime_data = []
        
        # Debug info
        self.last_request = None
        self.last_response = None
        self.last_error = None
        
    def load_anime_data(self, json_path):
        """
        Load anime data from a JSON file
        
        Args:
            json_path: Path to the JSON file containing anime data
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.anime_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading anime data: {e}")
            return False
    
    def get_anime_context(self, max_entries=15):
        """
        Format anime data as context for the LLM
        
        Args:
            max_entries: Maximum number of anime entries to include in context
            
        Returns:
            Formatted string with anime titles and synopsis
        """
        if not self.anime_data:
            return "No anime data available."
        
        context = "Here is information about anime from the Winter 2025 season:\n\n"
        
        # Limit the number of entries to avoid token limits
        for i, anime in enumerate(self.anime_data[:max_entries], 1):
            title = anime.get('title', 'Unknown Title')
            synopsis = anime.get('synopsis', 'No synopsis available')
            # Truncate synopsis if too long
            if len(synopsis) > 200:
                synopsis = synopsis[:200] + "..."
            context += f"{i}. {title}\nSynopsis: {synopsis}\n\n"
        
        return context
    
    def get_recommendations(self, user_query, temperature=0.7, max_tokens=1600, max_entries=10):
        """
        Get anime recommendations based on user query
        
        Args:
            user_query: User's query about anime recommendations
            temperature: Temperature parameter for the LLM (0.0 to 1.0)
            max_tokens: Maximum number of tokens in the response
            max_entries: Maximum number of anime entries to include in context
            
        Returns:
            LLM's response with recommendations
        """
        if not self.anime_data:
            return "Please load anime data first."
        
        # Create context with anime data
        anime_context = self.get_anime_context(max_entries=max_entries)
        
        # Create the prompt
        prompt = f"""You are an anime recommendation assistant. I'll provide you with information about anime from the Winter 2025 season.

{anime_context}

User Query: {user_query}

Please provide anime recommendations based on the user's query. PRIORITIZE recommending anime from the Winter 2025 list I provided above.

For each recommendation, explain why it might be a good match for the user.
"""
        
        # Store the request for debugging
        self.last_request = {
            "model": self.model_id,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            print(f"Sending request to OpenRouter API with model: {self.model_id}")
            print(f"Prompt length: {len(prompt)} characters")
            
            # Add a small delay before making the API call
            time.sleep(1)
            
            # Call the OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are an anime recommendation assistant with knowledge of anime across all seasons. You prioritize recommending anime from the current season when appropriate, but can also suggest anime from other seasons when relevant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Store the response for debugging
            self.last_response = {
                "model": response.model,
                "usage": {
                    "completion_tokens": response.usage.completion_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "content": response.choices[0].message.content if response.choices else "No content"
            }
            
            print(f"Response received from OpenRouter API:")
            print(f"Model: {response.model}")
            print(f"Tokens: {response.usage.completion_tokens} completion, {response.usage.prompt_tokens} prompt, {response.usage.total_tokens} total")
            
            # Check if we got a valid response
            if not response.choices or not response.choices[0].message.content:
                print("Warning: Empty response content from API")
                return "The API returned an empty response. Please try again with a different query or check your API key."
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Store the error for debugging
            self.last_error = str(e)
            print(f"Error getting recommendations: {e}")
            return f"Error getting recommendations: {e}"
    
    def get_debug_info(self):
        """
        Get debug information about the last API call
        
        Returns:
            Dictionary with debug information
        """
        return {
            "last_request": self.last_request,
            "last_response": self.last_response,
            "last_error": self.last_error
        } 