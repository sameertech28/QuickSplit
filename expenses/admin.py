from django.contrib import admin
from .models import Expense, ExpenseSplit


class ExpenseSplitInline(admin.TabularInline):
    model = ExpenseSplit
    extra = 1


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'paid_by', 'amount', 'currency', 'category', 'split_method', 'is_settled', 'date')
    list_filter = ('category', 'split_method', 'is_settled', 'currency')
    search_fields = ('title', 'description')
    inlines = [ExpenseSplitInline]


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense', 'user', 'amount', 'is_settled')
    list_filter = ('is_settled',)
