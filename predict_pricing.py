import pandas as pd
import numpy as np
from datetime import datetime

def calculate_future_price(base_price, start_date, monthly_escalation_rate=0.005):
    """
    Predicts future price with a confidence score.
    monthly_escalation_rate: 0.5% (0.005) is a standard construction inflation estimate.
    """
    # 1. Calculate months from today
    today = datetime.now()
    delta = (start_date - today).days / 30
    
    # 2. Calculate escalated price
    future_price = base_price * ((1 + monthly_escalation_rate) ** delta)
    
    # 3. Calculate Confidence Score (1.0 = certain, 0.0 = total guess)
    # Confidence drops as time increases (decay factor)
    confidence = max(0.1, 1.0 - (delta / 24)) # 24 months is the horizon
    
    return round(future_price, 2), round(confidence, 2)

# --- Example Usage ---
# Assume the project starts in 12 months
target_date = datetime(2027, 5, 25) 
price, conf = calculate_future_price(1000.00, target_date)

print(f"Predicted Price: ${price}")
print(f"Confidence Score: {conf * 100}%")
