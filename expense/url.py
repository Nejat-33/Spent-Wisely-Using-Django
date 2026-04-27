from django.urls import path
from .views import dashboard, signup, add_expense, update_expense, delete_expense, add_category, expense
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('login/', auth_views.LoginView.as_view(template_name='expenses/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', signup, name='signup'),
    path('add/', add_expense, name='add_expense'),
    path('edit/<int:pk>/', update_expense, name='edit_expense'),
    path('delete/<int:pk>/', delete_expense, name='delete_expense'),
    path('add_category/', add_category, name="add_category"),
    path('expense/', expense, name='expense')
]