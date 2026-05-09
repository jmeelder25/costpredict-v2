import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- INITIALIZE GEMINI CLIENT ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    client = genai.Client(api_key=API_KEY)

class ProjectQuery(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# --- SYSTEM INSTRUCTION (CP's Persona) ---
SYSTEM_PROMPT = """
You are 'CP', the official predictive pricing assistant for CostPredict. 
Your tagline is 'Pricing Made Predictive'.
Your goal is to provide highly accurate, data-driven cost forecasts for construction materials.
When given a Location, Date, and Category:
1. Analyze regional economic factors for that specific location.
2. Forecast price changes based on 2026 market trends, supply chain data, and inflation.
3. Provide a 'Confidence Score' for your prediction.
4. Keep your response structured, professional, and helpful.
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # In the latest FastAPI, 'request' must be passed explicitly like this:
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )

@app.post("/estimate")
async def generate_prediction(query: ProjectQuery):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key is missing.")
    
    prompt = f"User Request: {query.material_category} in {query.location} for {query.purchase_date}."
    
    try:
        # UPDATED BACK TO FULL FLASH
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
            contents=prompt
        )
        return {"prediction": response.text}
    except Exception as e:
        return {"error": str(e)}
