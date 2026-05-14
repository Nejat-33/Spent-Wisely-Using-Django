from django.urls import path
from .views import dashboard, signup, predict_category, add_expense,manage_categories, update_expense, delete_expense, add_category, expense, expense_detail, set_budget
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('login/', auth_views.LoginView.as_view(template_name='expenses/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', signup, name='signup'),
    path('add/', add_expense, name='add_expense'),
    path('edit/<int:pk>/', update_expense, name='edit_expense'),
    path('delete/<int:pk>/', delete_expense, name='delete_expense'),
    path('expense/', expense, name='expense'),
    path('set_budget', set_budget, name='set_budget'),
    path('expense_detail/<int:id>/', expense_detail, name='expense_detail'),
    path('manage_category/', manage_categories, name='manage_category'),
    path("predict-category/", predict_category, name="predict_category")
]