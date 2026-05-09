import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# 1. Mount the static folder so the logo displays correctly
# Ensure your image is at static/logo.png on GitHub
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize the Gemini Client
# Make sure GEMINI_API_KEY is set in your Render Environment Variables
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serving the Home Page
# We use a manual read here to avoid the Jinja2 'unhashable dict' error
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    if not os.path.exists(template_path):
        return HTMLResponse(content="Error: templates/index.html not found.", status_code=404)
    
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# 4. The Predictive Pricing Logic
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    prompt = (
        f"You are CostPredict (CP), an expert construction market analyst. "
        f"Provide a predictive pricing forecast for {req.material_category} "
        f"in {req.location} for the date {req.purchase_date}. "
        f"Include estimated price trends (up/down %), regional factors, "
        f"and a brief professional recommendation for a contractor. "
        f"Keep the response concise and professional."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            )
        )
        return {"prediction": response.text}
    except Exception as e:
        # This will show the actual error in the browser if the AI call fails
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
