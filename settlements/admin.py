from django.contrib import admin
from .models import Settlement


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'group', 'amount', 'currency', 'payment_method', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'payment_method', 'currency')
    search_fields = ('from_user__username', 'to_user__username', 'notes')
