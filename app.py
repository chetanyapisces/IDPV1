from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import get_reviews_dataframe
from logic import find_best_destination, get_itinerary
from pydantic import BaseModel
from typing import List

# Controller (Backend Application)
app = FastAPI(title="AI Itinerary Controller API")

# Mount Static View Layer
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request Model definitions
class ItineraryRequest(BaseModel):
    city: str
    attributes: List[str]
    days: int

@app.get("/")
async def root():
    """Serves the front-end view index."""
    return FileResponse('static/index.html')

@app.post("/api/generate_itinerary")
async def generate_itinerary_api(req: ItineraryRequest):
    """
    MVC Controller Endpoint: 
    Accepts City and Attributes -> Triggers Logic NLP -> Fetches Itinerary -> Returns Data
    """
    try:
        # Step 1: Model interaction
        df = get_reviews_dataframe()
        if df.empty:
            raise HTTPException(status_code=500, detail="Database returned no records. Ensure Firestore is populated.")

        # Step 2: NLP Match finding logic
        destination = find_best_destination(df, preferred_city=req.city, attributes_list=req.attributes)
        
        # Step 3: LLM Itinerary Generation logic
        final_itinerary = get_itinerary(destination['Place'], destination['City'], req.days)
        
        # Step 4: Return payload to View
        return {
            "success": True,
            "destination": destination,
            "financial_estimate": final_itinerary['price_estimate'],
            "itinerary": final_itinerary['itinerary']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
