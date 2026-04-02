import pandas as pd
from firebase_manager import fetch_dataframe_from_firebase

# Cache the dataframe locally to prevent unnecessary repetitive database hits
# in a production environment, you might use Redis or a scheduled task.
_cached_df = None

def get_reviews_dataframe():
    """
    Model function: Fetches the 'reduced_reviews' dataset from Firestore and returns it.
    Uses basic in-memory caching to avoid hitting the 50k document read limits multiple times.
    """
    global _cached_df
    if _cached_df is not None:
        print("Using cached DataFrame!")
        return _cached_df
    
    # Otherwise fetch from Firestore via our existing manager
    _cached_df = fetch_dataframe_from_firebase('reduced_reviews')
    return _cached_df
