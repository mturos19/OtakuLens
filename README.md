# OtakuLens - Anime Recommendation System

OtakuLens is an AI-powered anime recommendation system that helps you discover new anime from the Winter 2025 season based on your preferences. The application scrapes anime data from livechart.me and uses the DeepSeekR1Free model via OpenRouter to provide personalized recommendations.

## Features

- Web scraping of anime data from livechart.me
- AI-powered anime recommendations using DeepSeekR1Free via OpenRouter
- User-friendly Streamlit interface
- Save and load anime data in JSON format

## Prerequisites

- Python 3.8+
- OpenRouter API key (get one from [OpenRouter](https://openrouter.ai/))

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/OtakuLens.git
cd OtakuLens
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run src/app.py
```

2. In the sidebar, enter your OpenRouter API key.

3. Click "Scrape New Anime Data" to fetch the latest anime data from livechart.me, or select an existing JSON file if you've already scraped data.

4. Enter your query in the text area (e.g., "I watched 'Demon Slayer' and enjoyed it. What similar anime is available this season?").

5. Click "Get Recommendations" to receive personalized anime recommendations.

## Project Structure

```
OtakuLens/
├── data/                  # Directory for storing scraped anime data
├── src/
│   ├── app.py             # Streamlit frontend
│   ├── data_utils.py      # Utilities for scraping and processing anime data
│   ├── llm_utils.py       # Utilities for interacting with the LLM API
│   └── scrape_anime.py    # Script for scraping anime data
└── README.md              # This file
```

## How It Works

1. **Data Collection**: The application scrapes anime data (titles, synopsis, etc.) from livechart.me for the Winter 2025 season.

2. **Data Storage**: The scraped data is stored in JSON format in the `data/` directory.

3. **Recommendation Engine**: When you enter a query, the application sends it along with the anime data to the DeepSeekR1Free model via OpenRouter, which generates personalized recommendations based on your preferences.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [livechart.me](https://www.livechart.me/) for providing anime data
- [OpenRouter](https://openrouter.ai/) for providing access to the DeepSeekR1Free model
- [Streamlit](https://streamlit.io/) for the web application framework
