from django.contrib import admin
from .models import Expense, Contribution


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'created_by', 'amount', 'currency', 'category', 'date')
    list_filter = ('category', 'currency', 'group')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('user', 'expense', 'amount', 'note', 'created_at')
    list_filter = ('expense__group',)
    search_fields = ('user__username', 'note')
    date_hierarchy = 'created_at'
