import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount Static Files (For logo.png)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini Client
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# We use 'v1' to ensure we are on the stable production track
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=types.HttpOptions(api_version='v1')
)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve the User Interface (index.html)
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
        return {"error": "API Key missing. Check Render Environment Variables."}

    prompt = (
        f"You are CostPredict (CP), a construction economist. "
        f"Analyze {req.material_category} price trends for {req.location} on {req.purchase_date}. "
        f"Provide a percentage trend, regional analysis, and a buy/wait strategy."
    )
    
    try:
        # Using 'gemini-2.0-flash' which is the 2026 stable workhorse.
        # This resolves the 404 error you were seeing with the retired 1.5 model.
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "Market Data Error: Empty response from AI."}
            
    except Exception as e:
        return {"error": f"Market Data Error: {str(e)}"}

# 5. Port Configuration for Render
if __name__ == "__main__":
    import uvicorn
    # Render requires the app to listen on the port they provide
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
