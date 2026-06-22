import json
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, Bet, Transaction, Ticket


# ─────────────────────────── AUTH VIEWS ────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('game')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('game')
        return render(request, 'game/login.html', {'error': 'Username atau password salah.'})
    return render(request, 'game/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('game')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        if password != confirm:
            return render(request, 'game/register.html', {'error': 'Password tidak cocok.'})
        if UserProfile.objects.filter(username=username).exists():
            return render(request, 'game/register.html', {'error': 'Username sudah digunakan.'})
        UserProfile.objects.create_user(username=username, password=password, balance=Decimal('1000.00'))
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return redirect('game')
    return render(request, 'game/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────── MAIN PAGES ────────────────────────────

@login_required
def game_view(request):
    return render(request, 'game/index.html')


@login_required
def dashboard_view(request):
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')[:20]
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'game/dashboard.html', {
        'bets': bets,
        'transactions': transactions,
        'tickets': tickets,
    })


# ─────────────────────────── GAME API ────────────────────────────

@login_required
@require_GET
def api_user(request):
    user = request.user
    return JsonResponse({'id': user.id, 'username': user.username, 'balance': float(user.balance)})


@login_required
@require_POST
def api_bet(request):
    data = json.loads(request.body)
    bet_amount = Decimal(str(data.get('bet_amount', 0)))
    if bet_amount <= 0:
        return JsonResponse({'error': 'Jumlah taruhan tidak valid.'}, status=400)
    user = request.user
    if user.balance < bet_amount:
        return JsonResponse({'error': 'Saldo tidak cukup.'}, status=400)
    user.balance -= bet_amount
    user.save()
    bet = Bet.objects.create(user=user, bet_amount=bet_amount)
    return JsonResponse({'success': True, 'new_balance': float(user.balance), 'bet_id': bet.id})


@login_required
@require_POST
def api_cashout(request):
    data = json.loads(request.body)
    bet_id = data.get('bet_id')
    multiplier = Decimal(str(data.get('multiplier', 0)))
    percentage = int(data.get('percentage', 100))
    try:
        bet = Bet.objects.get(id=bet_id, user=request.user)
    except Bet.DoesNotExist:
        return JsonResponse({'error': 'Taruhan tidak ditemukan.'}, status=404)
    
    original_amount = bet.bet_amount
    user = request.user
    
    if percentage == 50:
        cashout_amount = original_amount * Decimal('0.5')
        remaining_amount = original_amount - cashout_amount
        winnings = cashout_amount * multiplier
        profit_half = winnings - cashout_amount
        
        # Update current bet to represent the cashed out 50%
        bet.bet_amount = cashout_amount
        bet.multiplier = multiplier
        bet.profit = profit_half
        bet.save()
        
        # Create a new active bet representing the remaining 50%
        new_bet = Bet.objects.create(
            user=user,
            bet_amount=remaining_amount,
            multiplier=Decimal('0.00'),
            profit=Decimal('0.00')
        )
        
        # Update user balance
        user.balance += winnings
        user.save()
        
        return JsonResponse({
            'success': True,
            'new_balance': float(user.balance),
            'profit': float(profit_half),
            'active_bet_id': new_bet.id
        })
    else:
        profit = original_amount * multiplier
        bet.multiplier = multiplier
        bet.profit = profit - original_amount
        bet.save()
        user.balance += profit
        user.save()
        return JsonResponse({'success': True, 'new_balance': float(user.balance), 'profit': float(profit - original_amount)})


@login_required
@require_POST
def api_crash(request):
    data = json.loads(request.body)
    bet_id = data.get('bet_id')
    try:
        bet = Bet.objects.get(id=bet_id, user=request.user)
        bet.multiplier = Decimal('0.00')
        bet.profit = -bet.bet_amount
        bet.save()
    except Bet.DoesNotExist:
        pass
    return JsonResponse({'success': True})


@login_required
@require_GET
def api_history(request):
    bets = Bet.objects.filter(user=request.user, multiplier__gt=0).order_by('-created_at')[:10]
    return JsonResponse([{'multiplier': float(b.multiplier)} for b in bets], safe=False)


# ─────────────────────────── TRANSACTION API ────────────────────────────

@login_required
@require_POST
def api_deposit(request):
    data = json.loads(request.body)
    amount = Decimal(str(data.get('amount', 0)))
    if amount <= 0:
        return JsonResponse({'error': 'Jumlah tidak valid.'}, status=400)
    # Auto-approve: langsung tambahkan saldo
    user = request.user
    user.balance += amount
    user.save()
    Transaction.objects.create(user=user, transaction_type='deposit', amount=amount, status='approved')
    return JsonResponse({'success': True, 'new_balance': float(user.balance)})


@login_required
@require_POST
def api_withdraw(request):
    data = json.loads(request.body)
    amount = Decimal(str(data.get('amount', 0)))
    if amount <= 0:
        return JsonResponse({'error': 'Jumlah tidak valid.'}, status=400)
    user = request.user
    if user.balance < amount:
        return JsonResponse({'error': 'Saldo tidak cukup.'}, status=400)
    user.balance -= amount
    user.save()
    Transaction.objects.create(user=user, transaction_type='withdraw', amount=amount, status='approved')
    return JsonResponse({'success': True, 'new_balance': float(user.balance)})


# ─────────────────────────── CUSTOMER SERVICE ────────────────────────────

@login_required
@require_POST
def api_submit_ticket(request):
    data = json.loads(request.body)
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()
    if not subject or not message:
        return JsonResponse({'error': 'Subject dan pesan tidak boleh kosong.'}, status=400)
    ticket = Ticket.objects.create(user=request.user, subject=subject, message=message)
    return JsonResponse({'success': True, 'ticket_id': ticket.id})
