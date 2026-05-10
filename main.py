import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount Static Files (Ensure you have a folder named 'static')
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini (Paid Tier / May 2026 Stable)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# --- THE MISSING PIECE: THE HOME ROUTE ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    try:
        if not os.path.exists(template_path):
            return HTMLResponse(content="Error: templates/index.html not found in GitHub.", status_code=404)
        
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Server Error: {str(e)}", status_code=500)

# 3. The Prediction Engine
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing."}

    try:
        # Using the stable 2026 alias for your paid account
        response = client.models.generate_content(
            model='gemini-flash-lite-latest', 
            contents=(
                f"As a construction economist, provide a pricing forecast for "
                f"{req.material_category} in {req.location} for {req.purchase_date}. "
                f"Include % change, market analysis, and procurement strategy."
            )
        )
        return {"prediction": response.text}
    except Exception as e:
        return {"error": f"Market Data Error: {str(e)}"}

# 4. Port Configuration for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
