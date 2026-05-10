import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# The v1 stable endpoint is required for the May 7th GA release.
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
        return {"error": "API Key is missing."}

    try:
        # AS OF MAY 7, 2026: gemini-3.1-flash-lite is the ONLY stable name.
        # Older 1.5 names are being actively retired from the v1 registry.
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=f"As a construction economist, predict {req.material_category} price trends for {req.location} on {req.purchase_date}."
        )
        return {"prediction": response.text}
    except Exception as e:
        # If this still returns 404, the issue is your API key's project permissions.
        return {"error": f"Service Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
