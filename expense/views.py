from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .expense.form import ExpenseForm
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from .models import Budget



@login_required
def dashboard(request):

    expense = Expense.objects.filter(user=request.user)
    total_sppent = expense.aggregate(Sum('amount'))['amount__sum'] or 0

    now = datetime.now()
    category = (
         expense.values('category').annotate(total_sum= Sum('amount')).order_by('-total_sum')
    )
    budget_obj = Budget.objects.filter(
         user = request.user,
         month = now.month,
         year = now.year
    ).first()

    budget_amount = budget_obj.amount if budget_obj else 0

    if budget_amount > 0:
         budget_percent = (total_sppent/ budget_amount) * 100
    else: 
         budget_percent = 0

    labels = [ item['category'] for item in category ]
    data = [float(item['total_sum']) for item in category]

    context = {
        "expenses" : expense,
        "total_spent": total_sppent,
        "labels": json.dumps(labels),
        "data": json.dumps(data),
        "budget_percent" : budget_percent,
        "budget_amount": min(budget_percent, 100),
        "is_over_budget" : total_sppent > budget_amount and budget_amount > 0
    }

    return render(request, 'expenses/dashboard.html', context)




def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'expenses/signup.html', {'form': form})



@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            return redirect('dashboard')
    else:
            form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})


@login_required
def update_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
            form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form})




@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
         expense.delete()
         return redirect('dashboard')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

