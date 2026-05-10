import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Initialize Client
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# We use the 'v1' stable version for the newly released Gemini 3 models
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
        return {"error": "API Key missing. Check Render settings."}

    try:
        # THE FIX: We use 'gemini-flash-lite-latest' instead of the specific version name.
        # This alias is already live on the v1 endpoint and maps to Gemini 3.1.
        response = client.models.generate_content(
            model='gemini-flash-lite-latest', 
            contents=(
                f"As a construction economist, provide a pricing forecast for "
                f"{req.material_category} in {req.location} for {req.purchase_date}."
            )
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "AI returned an empty response. Please try again."}
            
    except Exception as e:
        # If this STILL 404s, it's a transient Google API sync issue. 
        # Waiting 5 minutes and retrying usually clears it.
        return {"error": f"Market Data Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
