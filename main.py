import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Setup Static & Template Paths
# This ensures Render can find your logo and HTML files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client (Paid Tier / 2026 GA Stable)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# As of May 2026, we use the 'v1' stable API version
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve the UI (Homepage)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    if os.path.exists(template_path):
        # FileResponse is the fastest way to serve your static index.html
        return FileResponse(template_path)
    return HTMLResponse(content="Error: templates/index.html not found.", status_code=404)

# 4. The Prediction Engine (Using Gemini 3.1 Flash-Lite)
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Check Render environment variables."}

    try:
        # 'gemini-3.1-flash-lite' is the official stable model name 
        # released on May 7, 2026. This replaces all 2.0 and preview versions.
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=(
                f"Act as a construction economist for CostPredict. Analyze "
                f"{req.material_category} price trends for {req.location} on "
                f"{req.purchase_date}. Provide a percentage trend and strategy."
            )
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "The AI model responded, but the data was empty."}
            
    except Exception as e:
        # Logs the specific 2026 API error to your Render dashboard
        print(f"API Error: {str(e)}")
        return {"error": f"Market Data Error: {str(e)}"}

# 5. Port Configuration for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
