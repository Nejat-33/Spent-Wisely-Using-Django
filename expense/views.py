from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Category
from django.db.models import Sum, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .expense.form import ExpenseForm
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, timedelta
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
        form = ExpenseForm(request.POST, user = request.user)
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


@login_required
def manage_categories(request):
    categories = Category.objects.filter(user=request.user).order_by('name')
    
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            Category.objects.create(user=request.user, name=name)
            return redirect('dashboard')

    return render(request, 'expenses/manage_category.html', {
        'categories': categories
    })

@login_required
def add_category(request):
    if request.method == "POST":
          name = request.POST.get('name')
          if name:
               Category.objects.create(
                    name = name,
                    user = request.user
               )
               return redirect('dashboard')
    category = Category.objects.filter(user=request.user)
    return render(request, 'epenses/manage_category.html', {'category': category})



@login_required
def expense(request):
     now = datetime.now()

     period = request.GET.get('period')
     category_id = request.GET.get('category')
     query = request.GET.get('q')

     expense = Expense.objects.filter(
          user = request.user).order_by('-date')
     print(f"DEBUG: Found {expense.count()} total expenses for user {request.user}") # CHECK TERMINAL
    
     
     category = Category.objects.filter(user = request.user)

     if period == "today":
          expense = expense.filter(date = now.date())
     elif period == "this_month":
          expense = expense.filter(date__month = now.month)
     elif period == "last_week":
          last_week = now - timedelta(7)
          expense =expense.filter(date__gte = last_week)

     if category_id:
          expense = expense.filter(category = category_id)

     if query:
          expense = expense.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
     ) 
 
     total_spent = expense.aggregate(Sum('amount'))['amount__sum'] or 0
     print(f"DEBUG: Total spent is {total_spent}") 
     number_of_expense = expense.count()
    
     budget = Budget.objects.filter(user= request.user, month= now.month, year = now.year).first()
     average = round(total_spent/number_of_expense, 2) if number_of_expense > 0 else 0

     budget_amount = 0
     remaining_amount = 0

     if budget:
        budget_amount = budget.amount

     budget_exist = budget_amount > 0

     critical_alert = False

     if budget_exist:
          remaining_amount = budget_amount - total_spent
          remaining_percent = (remaining_amount / budget_amount) * 100


          if remaining_percent < 25:
               critical_alert = True
     
     
    
     context = {
          "expenses" : expense,
          "categories": category,
          "current_period": period,
          "current_category": category_id,
          "budget_amount" : budget_amount,
          "remaining_amount" : remaining_amount,
          "Total_spent" : total_spent,
          "Number_of_expense" : number_of_expense,
          "average_expense": average,
          "Current_month": now.strftime('%B %Y'),
          "critical_alert": critical_alert,
          "query": query
     }

     print ("expenses: ", context)
     return render(request, 'expenses/expense.html', {"expense_data" : context})

@login_required
def set_budget(request):
     now = datetime.now()
     budget_obj, create = Budget.objects.get_or_create(user= request.user,
                                                        month = now.month,
                                                          year=now.year,
                                                          defaults={"amount": 0})

     if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
             budget_obj.amount = amount
             budget_obj.save()
             return redirect('dashboard')
     return  render(request, 'expenses/set_budget.html', {"budget": budget_obj, 
                                                     "month": now.strftime('%B'), 
                                                     "year": now.year})


from django.shortcuts import render, get_object_or_404
from .models import Expense

@login_required
def expense_detail(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    
    return render(request, 'expenses/expense_detail.html', {'expense': expense})