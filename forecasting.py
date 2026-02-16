import pandas as pd
import numpy as np
from datetime import timedelta

def calculate_moving_averages(df, window_days=7):
    """
    Calculates moving average for the given DataFrame.
    Assumes df has 'date' and 'amount' columns and is sorted by date.
    """
    df_sorted = df.sort_values(by="date").copy()
    df_sorted = df_sorted.set_index("date")
    
    # Resample to daily to handle missing days
    daily_spend = df_sorted["amount"].resample("D").sum().fillna(0)
    
    ma = daily_spend.rolling(window=window_days).mean()
    return daily_spend, ma

def predict_next_month_spending(df):
    """
    Simple projection based on recent average spending.
    """
    if df.empty:
        return 0.0, 0.0

    # Get data for the last 30 days
    last_date = df["date"].max()
    start_date = last_date - timedelta(days=30)
    
    recent_df = df[df["date"] >= start_date]
    
    if recent_df.empty:
        return 0.0, 0.0

    total_recent = recent_df["amount"].sum()
    days_present = (last_date - start_date).days + 1
    
    # Simple daily average * 30
    daily_avg = total_recent / max(1, days_present)
    predicted_spend = daily_avg * 30
    
    return predicted_spend, daily_avg

def predict_spending_polynomial(df, degree=2):
    """
    Uses polynomial regression (numpy.polyfit) for a smoother trend forecast.
    """
    if df.empty or len(df) < 5:
        return None

    # Prepare data: X = days since start, Y = cumulative spend
    # Note: We fit on cumulative to see the "pace", or daily to see trend. 
    # Let's fit on Daily Spend to see if it's increasing.
    
    daily = df.set_index("date").resample("D")["amount"].sum().fillna(0).reset_index()
    daily["days_from_start"] = (daily["date"] - daily["date"].min()).dt.days
    
    X = daily["days_from_start"].values
    y = daily["amount"].values

    try:
        # Fit polynomial
        coeffs = np.polyfit(X, y, degree)
        poly = np.poly1d(coeffs)
        
        # Predict next 30 days
        last_day = X.max()
        future_days = np.arange(last_day + 1, last_day + 31)
        future_dates = [daily["date"].min() + timedelta(days=int(d)) for d in future_days]
        predicted_values = poly(future_days)
        
        # Clip negative predictions to 0
        predicted_values = np.maximum(predicted_values, 0)
        
        return pd.DataFrame({
            "date": future_dates,
            "predicted_amount": predicted_values
        })
    except Exception as e:
        print(f"Prediction Error: {e}")
        return None