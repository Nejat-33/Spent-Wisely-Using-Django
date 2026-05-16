# expenses/ml/spending_predictor.py

import numpy as np
from datetime import date, timedelta
from collections import defaultdict
from ..models import Expense


def get_weekly_spending(user):
    """
    Groups the user's expenses into weeks (week 1–4 of current month)
    and returns actual + predicted spending per week.
    """
   

    today = date.today()
    month_start = today.replace(day=1)

    expenses = Expense.objects.filter(
        user=user,
        date__gte=month_start,
        date__lte=today,
    ).values("date", "amount")

    if not expenses.exists():
        if today.month == 1:
            last_month_start = today.replace(year=today.year - 1, month=12, day=1)
        else:
            last_month_start = today.replace(month=today.month - 1, day=1)

        expenses = Expense.objects.filter(
            user=user,
            date__gte=last_month_start,
            date__lt=month_start,
        ).values("date", "amount")

        using_last_month = True
    else:
        using_last_month = False

    weekly_totals = defaultdict(float)
    for expense in expenses:
        day = expense["date"].day
        week_number = (day - 1) // 7 + 1  
        weekly_totals[week_number] += float(expense["amount"])
    if not weekly_totals:
        return {
            "actual": [],
            "predicted": [],
            "trend": "stable",
            "message": "No expenses found. Add some expenses to see your trend.",
        }
    current_week = (today.day - 1) // 7 + 1 if not using_last_month else 4

    actual_weeks  = sorted(weekly_totals.keys())
    actual_totals = [weekly_totals[w] for w in actual_weeks]

    for week in range(1, current_week + 1):
        actual_weeks.append(week)
        actual_totals.append(weekly_totals.get(week, 0.0))

    result = {
        "actual": [
            {"week": f"Week {w}", "amount": round(weekly_totals[w], 2)}
            for w in actual_weeks
        ],
        "predicted": [],
        "trend": "stable",
        "message": "Showing last month's data — add expenses this month to see current predictions." if using_last_month else "",
    }

    if len(actual_weeks) < 2:
        result["message"] = "Keep adding expenses — predictions appear after 2 weeks of data."
        return result

    x = np.array(actual_weeks, dtype=float)
    y = np.array(actual_totals, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)

    predicted = []
    for week in range(max(actual_weeks) + 1, 5):
        predicted_amount = slope * week + intercept
        predicted.append({
            "week": f"Week {week}",
            "amount": round(max(predicted_amount, 0), 2), 
        })


    result["predicted"] = predicted

    if actual_totals and predicted:
        last_actual = actual_totals[-1]
        next_predicted = predicted[0]["amount"]  

        if last_actual > 0:
            pct_change = ((next_predicted - last_actual) / last_actual) * 100
        else:
            pct_change = 100.0 if next_predicted > 0 else 0.0

        abs_pct = round(abs(pct_change))
        
        if next_predicted < 50.0:
            result["trend"] = "stable"
            result["message"] = "Your spending is holding steady at a very low and controlled amount. Excellent job!"
        
        elif pct_change > 5:
            result["trend"] = "increasing"
            result["message"] = f"Heads up! You are **on track to spend {abs_pct}% more** next week compared to this week. Consider cutting back on non-essentials."
        
        elif pct_change < -5:
            result["trend"] = "decreasing"
            result["message"] = f"Great job! Your spending is **on track to drop by {abs_pct}%** next week. Keep it up!"
        
        else:
            result["trend"] = "stable"
            result["message"] = "Your spending is holding steady. Next week is **expected to match** your current weekly average."
    return result