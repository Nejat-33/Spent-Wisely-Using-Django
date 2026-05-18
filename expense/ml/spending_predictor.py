
import numpy as np
from datetime import date
from collections import defaultdict
from ..models import Expense



def get_weekly_spending(user, budget_amount=0):
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
            "budget_status": None,
            "budget_message": "Set a monthly budget to see if you're on track.",
            "message": "No expenses found. Add some expenses to see your trend.",
        }

    current_week  = (today.day - 1) // 7 + 1 if not using_last_month else 4
    days_passed   = today.day if not using_last_month else 30
    total_spent   = sum(weekly_totals.values())
    daily_average = total_spent / max(days_passed, 1)
    projected_total = round(daily_average * 30, 2)

    actual_weeks  = sorted(weekly_totals.keys())
    actual_totals = [weekly_totals[w] for w in actual_weeks]

    result = {
        "actual": [
            {"week": f"Week {w}", "amount": round(weekly_totals[w], 2)}
            for w in actual_weeks
        ],
        "predicted": [],
        "trend": "stable",
        "summary": {
            "spent_so_far":    round(total_spent, 2),
            "daily_average":   round(daily_average, 2),
            "projected_total": projected_total,
            "days_passed":     days_passed,
            "days_remaining":  30 - days_passed,
        },
        "message": "",
        "budget_status":  None,
        "budget_message": "",
    }

    if using_last_month:
        result["message"] = "Showing last month's data — add expenses this month to see current predictions."

    elif len(actual_weeks) < 2:
        days_remaining       = 30 - days_passed
        remaining_projected  = round(daily_average * days_remaining, 2)
        future_weeks         = list(range(current_week + 1, 5))
        per_week_amount      = round(remaining_projected / max(len(future_weeks), 1), 2)

        for week in future_weeks:
            result["predicted"].append({
                "week": f"Week {week}",
                "amount": per_week_amount,
            })

        result["trend"]   = "stable"
        result["message"] = (
            f"You've spent ${total_spent:,.2f} in {days_passed} days "
            f"(~${daily_average:,.2f}/day). "
            f"Projected monthly total: ~${projected_total:,.2f}."
        )

    else:
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
            last_actual = actual_totals[-1]
            next_pred   = predicted[0]["amount"]
            pct_change  = ((next_pred - last_actual) / last_actual * 100) if last_actual > 0 else 0
            abs_pct     = round(abs(pct_change))

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

    if budget_amount > 0:
        projected = projected_total
        spent     = round(total_spent, 2)

        if spent > budget_amount:
            result["budget_status"]  = "exceeded"
            result["budget_message"] = f"⚠️ You've already exceeded your ${budget_amount:,.2f} budget — you're ${spent - budget_amount:,.2f} over."
        elif projected > budget_amount:
            result["budget_status"]  = "at_risk"
            result["budget_message"] = f"🚨 At this rate you'll exceed your ${budget_amount:,.2f} budget by ~${projected - budget_amount:,.2f} this month."
        elif projected > budget_amount * 0.85:
            result["budget_status"]  = "warning"
            result["budget_message"] = f"⚠️ You're on track to use {round((projected / budget_amount) * 100)}% of your ${budget_amount:,.2f} budget."
        else:
            result["budget_status"]  = "safe"
            result["budget_message"] = f"✅ You're on track to stay within your ${budget_amount:,.2f} budget this month."
    else:
        result["budget_status"]  = None
        result["budget_message"] = "Set a monthly budget to see if you're on track."

    return result