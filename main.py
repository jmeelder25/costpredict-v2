import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount Static Files
# This ensures your logo.png displays correctly.
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client
# The API key is pulled from your Render Environment Variables.
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve the User Interface
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    try:
        if not os.path.exists(template_path):
            return HTMLResponse(content="Error: templates/index.html not found.", status_code=404)
        
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Server Error: {str(e)}", status_code=500)

# 4. The Prediction Engine
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Please set GEMINI_API_KEY in Render."}

    # Since there's no spreadsheet, we instruct the AI to use its 
    # vast knowledge of regional market trends and supplier data.
    prompt = (
        f"You are CostPredict (CP), a professional construction economist. "
        f"Generate a detailed pricing forecast for {req.material_category} "
        f"in the {req.location} market for the date {req.purchase_date}. "
        f"\n\nContextual Data Sources: "
        f"Analyze trends from Home Depot, Lowe's, Metals Depot, and regional supply chains. "
        f"\n\nRequired Output Format: "
        f"### Predicted Price Trend "
        f"(State expected % change) "
        f"\n\n### Regional Market Analysis "
        f"(Mention factors specific to {req.location}) "
        f"\n\n### Procurement Strategy "
        f"(Advise to 'Buy Now', 'Wait', or 'Lock-in Contract' based on volatility)."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
            )
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "The AI engine is temporarily unresponsive. Please try again."}
            
    except Exception as e:
        # This catches things like 'Quota Exceeded' or 'Invalid Key'
        return {"error": f"Market Data Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
