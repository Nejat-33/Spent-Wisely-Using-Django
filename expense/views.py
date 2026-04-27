from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .expense.form import ExpenseForm
from django.contrib.auth.decorators import login_required
import json


def dashboard(request):
    expense = Expense.objects.filter(user=request.user)

    total_sppent = expense.aggregate(Sum('amount'))['amount__sum'] or 0

    category = (
         expense.values('category_name').annotate(total_sum= Sum('amount')).order_by('-total')
    )

    labels = [ item['category_name'] for item in category ]
    data = [float(item['total']) for item in category]

    context = {
        "expenses" : expense,
        "total_spent": total_sppent,
        "labels": json.dumps(labels),
        "data": json.dumps(data)
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
    return render(request, 'expense/edit_expense.html', {'form': form})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
         expense.delete()
         return redirect('dashboard')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

         