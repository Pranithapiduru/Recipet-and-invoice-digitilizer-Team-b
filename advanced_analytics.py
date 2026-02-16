import pandas as pd
from datetime import timedelta

def detect_subscriptions(df):
    """
    Identifies potential subscriptions based on recurring payments.
    Criteria:
    - Same vendor
    - At least 2 transactions
    - Amount variance < 10%
    - Time gap roughly 28-31 days (monthly) or 7 days (weekly)
    """
    if df.empty:
        return pd.DataFrame()

    df = df.sort_values(by=["vendor", "date"])
    subscriptions = []

    from typing import cast, Any
    for vendor, group in df.groupby("vendor"):
        # Explicitly cast group to DataFrame to satisfy Pyright/Pylance
        group = cast(pd.DataFrame, group)
        if len(group) < 2:
            continue
        
        # Check amount consistency (std dev low or all within 10% of mean)
        amounts = cast(pd.Series, group["amount"])
        mean_amt = float(amounts.mean())
        if mean_amt == 0: 
            continue
            
        # If variance is low (e.g., mostly same amount)
        # We allow small fluctuations (currency conversion, slight bill changes)
        if amounts.std() / mean_amt < 0.15: 
            
            # Check date gaps
            dates = cast(pd.Series, group["date"])
            diff_series = dates.diff()
            if diff_series is None:
                continue
            
            diffs = cast(pd.Series, diff_series.apply(lambda x: x.days if pd.notna(x) else None)).dropna()
            
            if diffs.empty:
                continue

            avg_gap = float(diffs.mean())
            
            # Monthly (approx 30 days) or Weekly (7 days)
            if (26 <= avg_gap <= 34) or (6 <= avg_gap <= 8):
                max_date = dates.max()
                if max_date is not None:
                    subscriptions.append({
                        "Vendor": vendor,
                        "Avg Amount": mean_amt,
                        "Frequency": "Monthly" if avg_gap > 20 else "Weekly",
                        "Next Due": max_date + timedelta(days=int(avg_gap)),
                        "Confidence": "High" if len(group) > 3 else "Medium"
                    })

    return pd.DataFrame(subscriptions)

def calculate_burn_rate(current_spend, monthly_budget, days_passed, total_days_in_month=30):
    """
    Calculates spending speed and status.
    """
    if monthly_budget <= 0:
        return None

    spend_per_day = current_spend / max(1, days_passed)
    projected_spend = spend_per_day * total_days_in_month
    
    status = "On Track"
    if projected_spend > monthly_budget:
        status = "Over Budget ⚠️"
    elif projected_spend < monthly_budget * 0.8:
        status = "Under Budget 🟢"
    
    return {
        "budget": monthly_budget,
        "current": current_spend,
        "remaining": monthly_budget - current_spend,
        "percent_used": min(100, (current_spend / monthly_budget) * 100),
        "status": status,
        "projected": projected_spend
    }