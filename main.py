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

# THE MAY 10 FIX: Using 'v1beta' instead of 'v1'
# New models like 3.1 Flash-Lite often live here for the first 14 days of GA.
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1beta')
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
        # Using the official stable name in the beta endpoint
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=f"As a construction economist, predict {req.material_category} price trends for {req.location} on {req.purchase_date}."
        )
        return {"prediction": response.text}
    except Exception as e:
        # This will now capture the specific reason if v1beta also rejects it
        return {"error": f"Service Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
