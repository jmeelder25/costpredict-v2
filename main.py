import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount the static folder for the logo
# Ensure your image is at static/logo.png on GitHub
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client
# Uses gemini-1.5-flash for better free-tier availability
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve Home Page
# Manual read avoids the Jinja2 template/dict caching bug
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Error loading HTML: {str(e)}", status_code=500)

# 4. AI Pricing Logic
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    prompt = (
        f"You are CostPredict (CP), an expert construction market analyst. "
        f"Provide a predictive pricing forecast for {req.material_category} "
        f"in {req.location} for the date {req.purchase_date}. "
        f"Include estimated price trends (up/down %), regional factors, "
        f"and a brief professional recommendation for a contractor."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        return {"prediction": response.text}
    except Exception as e:
        return {"error": str(e)}
