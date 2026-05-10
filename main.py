import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Initialize Gemini Client
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# We use the modern client. If you still get 404, 
# the 'api_version' fix below is the magic key.
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Check Render Environment Variables."}

    prompt = f"Estimate {req.material_category} prices in {req.location} for {req.purchase_date}."
    
    try:
        # UPDATED: gemini-2.0-flash is the current stable standard for 2026.
        # It replaces 1.5-flash for general 'generate_content' calls.
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "AI returned an empty response."}
            
    except Exception as e:
        return {"error": f"Market Data Error: {str(e)}"}
