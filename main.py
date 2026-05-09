import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

app = FastAPI(title="CostPredict CP Assistant")

# --- INITIALIZE GEMINI CLIENT ---
# Render will get this from your Environment Variables
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class ProjectQuery(BaseModel):
    location: str
    purchase_date: str
    material_category: str

# --- SYSTEM INSTRUCTION ---
SYSTEM_PROMPT = """
You are 'CP', a professional AI predictive pricing assistant for CostPredict. 
Your goal is to provide highly accurate cost estimates for construction materials.
When given a Location, Date, and Category:
1. Consider regional cost differences (e.g., Chicago is more expensive than rural areas).
2. Predict future price fluctuations based on 2025-2026 economic trends (inflation, tariffs).
3. Provide a 'Confidence Score' as a percentage.
4. Keep the tone professional, helpful, and concise.
"""

@app.get("/")
def home():
    return {"message": "CP is online and connected to the predictive engine."}

@app.post("/estimate")
async def generate_prediction(query: ProjectQuery):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key is missing on the server.")
    
    prompt = f"Provide a predictive cost estimate. Location: {query.location}. Date: {query.purchase_date}. Category: {query.material_category}."
    
    try:
        response = client.models.generate_content(
            # CHANGED TO FLASH-LITE
            model="gemini-2.0-flash-lite", 
            config=types.GenerateContentConfig(
                system_instruction="You are CP, a professional construction cost predictor. Keep it concise."
            ),
            contents=prompt
        )
        return {"status": "Success", "prediction": response.text}
    except Exception as e:
        # If it still gives a 429, this will tell us exactly why
        return {"status": "Error", "message": str(e)}
