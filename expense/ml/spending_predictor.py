
import numpy as np
from datetime import date
from collections import defaultdict
from ..models import Expense




def get_weekly_spending(user):
    today = date.today()
    month_start = today.replace(day=1)

    expenses = Expense.objects.filter(
        user=user,
        date__gte=month_start,
        date__lte=today,
    ).values("date", "amount")

    using_last_month = False
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

    # Group into weeks
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
            "summary": None,
            "message": "No expenses found. Add some expenses to see your trend.",
        }

    current_week = (today.day - 1) // 7 + 1 if not using_last_month else 4
    days_passed = today.day if not using_last_month else 30
    total_spent = sum(weekly_totals.values())
    daily_average = total_spent / max(days_passed, 1)
    projected_total = round(daily_average * 30, 2)

    actual_weeks  = sorted(weekly_totals.keys())  # ← only built once, no duplicate loop
    actual_totals = [weekly_totals[w] for w in actual_weeks]

    result = {
        "actual": [
            {"week": f"Week {w}", "amount": round(weekly_totals[w], 2)}
            for w in actual_weeks
        ],
        "predicted": [],
        "trend": "stable",
        "summary": {
            "spent_so_far": round(total_spent, 2),
            "daily_average": round(daily_average, 2),
            "projected_total": projected_total,
            "days_passed": days_passed,
            "days_remaining": 30 - days_passed,
        },
        "message": "Showing last month's data — add expenses this month to see current predictions." if using_last_month else "",
    }

    if using_last_month:
        return result

    if len(actual_weeks) < 2:
        days_remaining = 30 - days_passed
        remaining_projected = round(daily_average * days_remaining, 2)

        future_weeks = list(range(current_week + 1, 5))
        per_week_amount = round(remaining_projected / max(len(future_weeks), 1), 2)

        for week in range(current_week + 1, 5):
          result["predicted"].append({
            "week": f"Week {week}",
            "amount": per_week_amount,
          })

        result["trend"] = "stable"
        result["message"] = (
            f"You've spent ${total_spent:,.2f} in {days_passed} days "
            f"(~${daily_average:,.2f}/day). "
            f"Projected monthly total: ~${projected_total:,.2f}."
        )
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

    if predicted:
        last_actual   = actual_totals[-1]
        next_pred     = predicted[0]["amount"]
        pct_change    = ((next_pred - last_actual) / last_actual * 100) if last_actual > 0 else 0
        abs_pct       = round(abs(pct_change))

        if next_pred < 50:
            result["trend"]   = "stable"
            result["message"] = "Your spending is very low and controlled. Excellent job!"
        elif pct_change > 5:
            result["trend"]   = "increasing"
            result["message"] = f"Heads up! You're on track to spend {abs_pct}% more next week. Consider cutting back on non-essentials."
        elif pct_change < -5:
            result["trend"]   = "decreasing"
            result["message"] = f"Great job! Your spending is on track to drop by {abs_pct}% next week. Keep it up!"
        else:
            result["trend"]   = "stable"
            result["message"] = "Your spending is holding steady — next week should match your current average."
    else:
        result["message"] = (
            f"You've spent ${total_spent:,.2f} in {days_passed} days "
            f"(~${daily_average:,.2f}/day). "
            f"Projected monthly total: ~${projected_total:,.2f}."
        )

    return result