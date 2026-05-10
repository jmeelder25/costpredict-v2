import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount Static Files
# This allows the app to serve your logo at /static/logo.png
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client
# This pulls your API key from the Environment Variables in Render
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

# 4. The Prediction Engine (Fixed Model Logic)
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Please set GEMINI_API_KEY in Render environment settings."}

    prompt = (
        f"You are CostPredict (CP), a professional construction economist. "
        f"Provide a predictive pricing forecast for {req.material_category} "
        f"in {req.location} for {req.purchase_date}. "
        f"\n\nMarket Intelligence Sources: "
        f"Analyze trends from Home Depot, Lowe's, Metals Depot, and regional suppliers. "
        f"\n\nOutput Requirements: "
        f"### Predicted Price Trend "
        f"State the expected % change. "
        f"\n\n### Regional Market Analysis "
        f"Identify factors specific to {req.location}. "
        f"\n\n### Procurement Strategy "
        f"Recommend: Buy Now, Wait, or Lock-in Contract."
    )
    
    try:
        # We use 'gemini-1.5-flash' directly to avoid the v1beta 404 error
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
            return {"error": "The AI engine returned an empty response. Please try again."}
            
    except Exception as e:
        # Captures API errors, quota limits, or connectivity issues
        return {"error": f"Market Data Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Render provides the PORT variable automatically
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
