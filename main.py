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

# We use the v1 stable client
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
        # STEP 1: Find an active model on your account
        # This bypasses the naming bugs Google is currently having.
        model_list = client.models.list()
        # Find the first 'flash' model that supports generating content
        target_model = next((m.name for m in model_list if 'flash' in m.name and 'generateContent' in m.supported_methods), None)

        if not target_model:
            return {"error": "No valid Flash models found on this API key."}

        # STEP 2: Use that model
        response = client.models.generate_content(
            model=target_model,
            contents=f"Price forecast for {req.material_category} in {req.location} on {req.purchase_date}."
        )
        return {"prediction": response.text}

    except Exception as e:
        return {"error": f"Diagnostic Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
