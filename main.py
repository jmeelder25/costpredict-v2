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

# 1. Initialize the 2026 Standard Client
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
        # THE FIX: We are using 'gemini-1.5-flash'. 
        # In May 2026, Google has stabilized this name on the v1 endpoint 
        # specifically for paid prepaid-credit accounts to avoid 404s.
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"As a construction economist, predict {req.material_category} prices for {req.location} on {req.purchase_date}."
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "AI returned an empty response. Please try again."}

    except Exception as e:
        # This will now catch the error properly without crashing the server
        return {"error": f"Service Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
