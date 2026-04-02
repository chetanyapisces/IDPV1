import os
import spacy
import re
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from google import genai

# Load env variables for API key securely
load_dotenv()

# We only load the NLP model once, not on every single request
print("Loading NLP Models...")
try:
    nlp = spacy.load('en_core_web_md')
except OSError:
    print("Warning: Spacy 'en_core_web_md' model not found. Trying to download or fallback.")
    # Fallback/stub warning for the server script
    nlp = None

analyzer = SentimentIntensityAnalyzer()
client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

def find_best_destination(df, preferred_city, attributes_list):
    """
    NLP Recommendation matching based on Vader Sentiment and Spacy Similarity
    """
    if df.empty:
        raise ValueError("The dataset is empty!")
        
    text = df.copy()
    
    # Preprocessing
    text['Review'] = text['Review'].fillna('')
    # NLP Similarity
    if len(attributes_list) > 0 and nlp is not None:
        target_doc = nlp(' '.join(attributes_list))
        text['Spacy Similarity'] = text['Review'].apply(lambda x: target_doc.similarity(nlp(str(x))))
    else:
        text['Spacy Similarity'] = 1.0 # Default value if no attributes or NLP missing
        
    # Vader Sentiment
    text['Sentiment'] = text['Review'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])
    text['Spacy Similarity x Sentiment'] = text['Spacy Similarity'] * text['Sentiment']

    # Aggregation
    aggregation_functions = {
        'City': 'first', 
        'Rating': 'mean',
        'Review': 'sum', 
        'Sentiment': 'mean',
        'Spacy Similarity': 'mean',
        'Spacy Similarity x Sentiment': 'mean'
    }
    
    # Filter by city (if provided)
    if preferred_city:
        pref = preferred_city.lower().strip()
        text['CityLower'] = text['City'].astype(str).str.lower()
        filt_text = text[text['CityLower'].str.contains(pref, na=False)]
        if filt_text.empty:
            filt_text = text # Fallback if no matching city found
    else:
        filt_text = text
        
    # Group by place to find the overall best
    agg_text = filt_text.groupby('Place').aggregate(aggregation_functions)
    agg_text = agg_text.sort_values(by='Spacy Similarity x Sentiment', ascending=False)
    
    if agg_text.empty:
        raise ValueError("Could not find any places matching criteria!")

    best_place_row = agg_text.iloc[0]
    return {
        "Place": agg_text.index[0],
        "City": best_place_row['City'],
        "Rating": round(float(best_place_row['Rating']), 1),
        "MatchScore": round(float(best_place_row['Spacy Similarity x Sentiment'] * 100), 2)
    }

def get_itinerary(place, city, days):
    """
    Controller function: Calls Gemini to generate the actual itinerary.
    """
    # 1. Price estimate
    price_prompt = f"Provide a concise financial estimate for a visit to {place} in {city}, accounting for entry fees and primary activities."
    price_res = client.models.generate_content(model='gemini-2.5-flash', contents=price_prompt)
    estimated_price = price_res.text
    
    # 2. Daily Itinerary
    itin_prompt = (
        f"Act as a professional logistical coordinator. "
        f"Formulate a structured {days}-day itinerary for a field expedition to {place} located in {city}. "
        f"Integrate the primary activities, strategic time allocations, and accommodate a financial parameter of: {estimated_price}. Format the result with cleanly structured markdown headers and bullet points."
    )
    itin_res = client.models.generate_content(model='gemini-2.5-flash', contents=itin_prompt)
    
    return {
        "price_estimate": estimated_price,
        "itinerary": itin_res.text
    }
