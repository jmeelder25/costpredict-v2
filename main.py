import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount the static folder for the logo
# Ensure your logo image is at static/logo.png on GitHub
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client
# We use gemini-1.5-flash for high reliability and speed
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve Home Page
# This manual method prevents the common Jinja2 'unhashable dict' error
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

# 4. AI Pricing Logic (Synced with Spreadsheet Data)
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    # Professional prompt referencing your specific spreadsheet sources
    prompt = (
        f"You are CostPredict (CP), a senior construction market analyst. "
        f"Your goal is to provide a predictive pricing forecast for {req.material_category} "
        f"in {req.location} for the target date {req.purchase_date}. "
        f"\n\nMarket Intelligence Sources: "
        f"Analyze trends from Home Depot, Lowe's, Metals Depot, LL Flooring, "
        f"Wholesale Cabinets, Floor & Decor, and Menards. "
        f"\n\nOutput Requirements: "
        f"1. Predicted Price Trend: State the expected percentage change. "
        f"2. Regional Analysis: Mention factors specific to {req.location}. "
        f"3. Procurement Strategy: Advise whether to buy now or wait based on supply chain health. "
        f"\n\nFormat the response professionally with clear headings."
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
            return {"error": "The AI engine returned an empty response. Please try again."}
            
    except Exception as e:
        # Catching rate limits (429) or connection issues
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
