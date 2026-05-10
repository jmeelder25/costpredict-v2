import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Static file mounting
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Paid Tier Client Initialization
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# The 'google-genai' library uses this Client structure for 2026 models
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
    if os.path.exists(template_path):
        return FileResponse(template_path)
    return HTMLResponse(content="index.html not found.", status_code=404)

@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key is missing from Render Environment Variables."}

    try:
        # We use the GA (General Availability) model name for May 2026
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=f"Price forecast for {req.material_category} in {req.location} on {req.purchase_date}."
        )
        return {"prediction": response.text}
    except Exception as e:
        # This will now give us a clear, non-cryptic error if something is still wrong
        return {"error": f"Connection Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
