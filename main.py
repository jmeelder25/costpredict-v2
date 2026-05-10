import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
# Using the 2026 Standard SDK
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount Static Files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini (Paid Tier / Gemini 3.1)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Explicitly setting api_version to 'v1' ensures we hit the stable May 2026 endpoint
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve the UI
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

# 4. The Prediction Engine (Using Gemini 3.1 Flash-Lite)
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Update Render Environment Variables."}

    try:
        # gemini-3.1-flash-lite is the new stable standard as of May 7, 2026.
        # It replaces the deprecated gemini-2.0-flash.
        prompt = (
            f"As a senior construction market analyst, provide a pricing forecast "
            f"for {req.material_category} in {req.location} for {req.purchase_date}. "
            f"Include predicted % change, regional market analysis, and a strategy."
        )

        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "The AI is processing but returned no text."}
            
    except Exception as e:
        return {"error": f"Market Data Error: {str(e)}"}

# 5. Port Configuration
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
