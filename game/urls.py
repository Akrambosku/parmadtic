from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.game_view, name='game'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Game API
    path('api/user/', views.api_user, name='api_user'),
    path('api/bet/', views.api_bet, name='api_bet'),
    path('api/cashout/', views.api_cashout, name='api_cashout'),
    path('api/crash/', views.api_crash, name='api_crash'),
    path('api/history/', views.api_history, name='api_history'),

    # Transaction API
    path('api/deposit/', views.api_deposit, name='api_deposit'),
    path('api/withdraw/', views.api_withdraw, name='api_withdraw'),

    # Customer Service
    path('api/ticket/', views.api_submit_ticket, name='api_ticket'),
]
