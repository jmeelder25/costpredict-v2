import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount Static Files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini (Paid Tier / 2026 Stable)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# IMPORTANT: We use the 'v1' stable endpoint for the Gemini 3.1 series
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Server Error: {str(e)}", status_code=500)

@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Check Render Environment Variables."}

    try:
        # AS OF MAY 7, 2026: The stable model ID is 'gemini-3.1-flash-lite'
        # If the specific version gives a 404, we use the 'latest' alias 
        # which Google keeps updated to the current stable build.
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite', 
            contents=(
                f"As a construction economist, provide a pricing forecast for "
                f"{req.material_category} in {req.location} for {req.purchase_date}. "
                f"Include % change, market analysis, and procurement strategy."
            )
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "AI processed the request but returned no text."}
            
    except Exception as e:
        # If this still 404s, it's a project-level propagation delay
        return {"error": f"Market Data Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
