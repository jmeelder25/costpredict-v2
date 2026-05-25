import pandas as pd
import numpy as np
from datetime import datetime
import os

class CostPredictor:
    def __init__(self, historical_data_path="data/historical"):
        self.data_path = historical_data_path
        # Volatility multipliers per category (higher = more risky/unstable)
        self.volatility_map = {
            "Lumber and Composites": 1.5,
            "Metals": 1.5,
            "Paint": 1.1,
            "Builders Hardware": 1.1,
            "Concrete and Cement and Masonry": 1.3
        }

    def get_forecast(self, category, item_name, base_price, start_date_str):
        """
        Calculates future price and confidence score.
        start_date_str: Format 'YYYY-MM-DD'
        """
        # 1. Configuration
        today = datetime.now()
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        months_out = max(0, (start_date - today).days / 30.44)
        
        # 2. Apply Monthly Escalation (e.g., 0.5% inflation per month)
        monthly_rate = 0.005 
        future_price = base_price * ((1 + monthly_rate) ** months_out)
        
        # 3. Calculate Confidence Score (Decay model)
        # Confidence drops as time increases, accelerated by category volatility
        volatility = self.volatility_map.get(category, 1.2) # Default 1.2
        confidence = max(0.1, 1.0 - (months_out / 24) * volatility)
        
        return round(future_price, 2), round(confidence, 2)

# --- Example Usage ---
if __name__ == "__main__":
    predictor = CostPredictor()
    
    # Input example
    category = "Lumber and Composites"
    current_price = 1500.00
    future_start = "2027-05-25"
    
    pred_price, conf = predictor.get_forecast(category, "SPF Dimensional Lumber", current_price, future_start)
    
    print(f"--- Prediction for {category} ---")
    print(f"Current Price: ${current_price}")
    print(f"Projected Price ({future_start}): ${pred_price}")
    print(f"Confidence Score: {int(conf * 100)}%")
