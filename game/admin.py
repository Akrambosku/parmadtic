from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Bet, Transaction, Ticket


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'email', 'balance', 'is_staff', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Game Data', {'fields': ('balance',)}),
    )


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'multiplier', 'profit', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__username',)
    actions = ['approve_transactions']

    @admin.action(description='Setujui transaksi terpilih')
    def approve_transactions(self, request, queryset):
        for tx in queryset.filter(status='pending'):
            tx.status = 'approved'
            tx.save()
            if tx.transaction_type == 'deposit':
                tx.user.balance += tx.amount
                tx.user.save()
            elif tx.transaction_type == 'withdraw':
                if tx.user.balance >= tx.amount:
                    tx.user.balance -= tx.amount
                    tx.user.save()


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'subject')
