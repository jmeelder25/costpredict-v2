import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# 1. Mount Static Files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Initialize Gemini (Paid Tier Configuration)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

class EstimateRequest(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# 3. Serve the UI
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = "templates/index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Server Error: {str(e)}", status_code=500)

# 4. The Prediction Engine (Using Gemini 2.0 Flash)
@app.post("/estimate")
async def get_estimate(req: EstimateRequest):
    if not GEMINI_KEY:
        return {"error": "API Key missing. Update Render Environment Variables."}

    try:
        # Since you are now a paid user, you can use the high-performance 2.0 model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = (
            f"Act as a senior construction market analyst. Provide a detailed price "
            f"forecast for {req.material_category} in {req.location} for {req.purchase_date}. "
            f"Include a predicted % change, a local market factor analysis, "
            f"and a specific procurement strategy (e.g., 'Bulk Buy Now' or 'Wait for Q3')."
        )

        # Paid tier allows for faster generation and higher safety settings
        response = model.generate_content(prompt)
        
        if response.text:
            return {"prediction": response.text}
        else:
            return {"error": "The AI is processing your request, but returned no text."}
            
    except Exception as e:
        # This will now catch very specific billing or limit errors if they occur
        return {"error": f"API Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
