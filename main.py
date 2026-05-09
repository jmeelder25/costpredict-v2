import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# Mount the static folder so the logo displays
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
current_dir = os.path.dirname(os.path.abspath(__file__))
# We are adding , context_processors=[] to fix the Python 3.14 compatibility issue
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize the Gemini Client using your API Key environment variable
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            )
        )
        return {"prediction": response.text}
    except Exception as e:
        return {"error": str(e)}
