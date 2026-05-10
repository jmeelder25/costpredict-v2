import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
# Using the modern Google GenAI SDK
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount Static Files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# FIX: We explicitly set the api_version to 'v1' to avoid the 404 v1beta error
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve the User Interface
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    try:
        if not os.path.exists(template_path):
            return HTMLResponse(content="Error: templates/index.html not found.", status_code=404)
        
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Server Error: {str(e)}", status_code=500)

# 4. The Prediction Engine
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Please set GEMINI_API_KEY in Render."}

    try:
        # Use the standard flash model name
        prompt = (
            f"You are CostPredict (CP), a senior construction economist. "
            f"Provide a predictive pricing forecast for {req.material_category} "
            f"in {req.location} for {req.purchase_date}. "
            f"\n\nOutput Format: "
            f"### Predicted Price Trend \n### Regional Market Analysis \n### Procurement Strategy"
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "The AI engine returned an empty response."}
            
    except Exception as e:
        return {"error": f"Market Data Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
