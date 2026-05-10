import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client (2026 Paid Tier Standard)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# We use the 'v1' stable endpoint
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve the UI via FileResponse
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    if os.path.exists(template_path):
        return FileResponse(template_path)
    return HTMLResponse(content="Error: index.html not found.", status_code=404)

# 4. The Prediction Engine
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing in Render settings."}

    try:
        # 'gemini-flash-lite-latest' is the auto-updating alias for May 2026.
        # This bypasses the specific 404 version errors.
        response = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents=(
                f"As a construction economist, predict {req.material_category} "
                f"prices for {req.location} on {req.purchase_date}."
            )
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "Model connected but returned no data."}
            
    except Exception as e:
        return {"error": f"API Connection Issue: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
