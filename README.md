# Flight Finder AI

An AI-powered flight search assistant that helps users find flights with natural language queries.

## Features

- Natural language flight search
- Dynamic price filtering
- Time-based filtering (morning, afternoon, night)
- Real-time flight data via Amadeus API
- AI-powered responses using Google's Gemini API

## Deployment to Railway.app

1. Create a Railway account at https://railway.app
2. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```
3. Login to Railway:
   ```bash
   railway login
   ```
4. Create a new project:
   ```bash
   railway init
   ```
5. Add environment variables in Railway dashboard:
   - GOOGLE_API_KEY
   - AMADEUS_API_KEY

6. Deploy the application:
   ```bash
   railway up
   ```

## Environment Variables

Make sure to set these environment variables in Railway:

- `GOOGLE_API_KEY`: Your Google Gemini API key
- `AMADEUS_API_KEY`: Your Amadeus API key
- `PORT`: Set automatically by Railway

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys
5. Run the application:
   ```bash
   chainlit run app.py
   ```

## Tech Stack

- Python 3.9
- Chainlit
- Google Gemini API
- Amadeus API
- Railway.app for deployment
