import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="CostPredict CP Assistant")

# --- DATA MODELS (The "Rules" for CP) ---

class ProjectQuery(BaseModel):
    # Question 1: Location
    location: str = Field(..., description="City, State or 5-digit Zip Code")
    
    # Question 2: Date
    purchase_date: str = Field(..., description="Month and Year (e.g., December 2026)")
    
    # Question 3: Material Category
    material_category: str = Field(..., description="Selected material category from the list")

    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        # Basic check: If it's a zip, must be 5 digits. If text, must have some length.
        if v.isdigit() and len(v) != 5:
            raise ValueError('Zip code must be exactly 5 digits.')
        return v

# --- CATEGORY LIST (From your Document) ---

MATERIAL_CATEGORIES = [
    "Lumber, Building Materials & Structural",
    "Exterior Construction",
    "Interior Construction",
    "Builders Hardware",
    "Decking",
    "Ceilings",
    "Cabinetry & Countertops",
    "Plumbing & Bath",
    "Paint, Finishes & Adhesives",
    "Tools",
    "Vanities",
    "Ventilation",
    "Windows"
]

# --- ROUTES ---

@app.get("/")
def read_root():
    return {
        "greeting": "Hello World! My name is CP, and I'm your trusted predictive pricing assistant.",
        "instructions": "To start, send a POST request to /estimate with your project details."
    }

@app.get("/categories")
def get_categories():
    """Returns the list for Question #3"""
    return {"categories": MATERIAL_CATEGORIES}

@app.post("/estimate")
async def create_estimate(query: ProjectQuery):
    """
    This is where the magic happens. 
    It takes the Location, Date, and Category and will eventually 
    send them to Gemini for the prediction.
    """
    # For now, CP just confirms the intake
    return {
        "status": "Success",
        "cp_response": f"Got it! I'm looking at {query.material_category} for a project in {query.location} planned for {query.purchase_date}.",
        "next_step": "Connecting to predictive engine..."
    }
