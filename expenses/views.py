from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Expense, Contribution
from .forms import ExpenseForm, ContributionForm
from .utils import extract_expense_from_receipt
from core.utils import convert_currency

from groups.models import Group, GroupMember
import tempfile
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def _is_group_member(user, group):
    return GroupMember.objects.filter(user=user, group=group).exists()


def _is_group_admin(user, group):
    return GroupMember.objects.filter(user=user, group=group, role='admin').exists()


@login_required
def expense_create(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    # Only admin can create expenses
    if not _is_group_admin(request.user, group):
        messages.error(request, "Only group admins can create expenses.")
        return redirect('groups:detail', pk=group.pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.created_by = request.user
            expense.save()
            

            messages.success(request, 'Expense added successfully!')
            return redirect('expenses:detail', pk=expense.pk)
    else:
        form = ExpenseForm(group=group)

    return render(request, 'expenses/expense_form.html', {
        'form': form, 'group': group, 'action': 'Add'
    })


from decimal import Decimal

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(
        Expense.objects.select_related('created_by', 'group'), pk=pk
    )
    group = expense.group

    # Must be a group member to view
    if not _is_group_member(request.user, group):
        messages.error(request, "You don't have access to this expense.")
        return redirect('dashboard')

    contributions = expense.contributions.select_related('user').all()
    contribution_form = ContributionForm()
    is_admin = _is_group_admin(request.user, group)

    # Calculate expected share and who hasn't paid their part for THIS expense
    members = group.group_members.select_related('user').all()
    num_members = members.count()
    expected_share = (expense.amount / Decimal(num_members)) if num_members > 0 else Decimal('0.00')

    missing_shares = []
    for member in members:
        paid = sum((c.amount for c in contributions if c.user_id == member.user_id), Decimal('0.00'))
        shortfall = round(expected_share - paid, 2)
        if shortfall > 0:
            missing_shares.append({
                'display_name': member.display_name,
                'shortfall': shortfall
            })

    converted_amount = None
    if expense.currency != group.currency:
        try:
            converted = convert_currency(expense.amount, expense.currency, group.currency)
            converted_amount = round(converted, 2)
        except Exception:
            pass

    return render(request, 'expenses/expense_detail.html', {
        'expense': expense,
        'converted_amount': converted_amount,
        'contributions': contributions,
        'contribution_form': contribution_form,
        'group': group,
        'is_admin': is_admin,
        'missing_shares': missing_shares,
    })


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    group = expense.group

    # Only admin can edit
    if not _is_group_admin(request.user, group):
        messages.error(request, "Only group admins can edit expenses.")
        return redirect('expenses:detail', pk=expense.pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, group=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses:detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense, group=group)

    return render(request, 'expenses/expense_form.html', {
        'form': form, 'group': group, 'action': 'Edit', 'expense': expense
    })


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    group = expense.group

    # Only admin can delete the entire expense
    if not _is_group_admin(request.user, group):
        messages.error(request, "Only group admins can delete expenses.")
        return redirect('expenses:detail', pk=expense.pk)

    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('groups:detail', pk=group.pk)

    return render(request, 'expenses/expense_confirm_delete.html', {
        'expense': expense, 'group': group
    })


@login_required
def contribution_add(request, expense_id):
    """Any group member can record their own contribution."""
    expense = get_object_or_404(Expense, pk=expense_id)
    group = expense.group

    if not _is_group_member(request.user, group):
        messages.error(request, "You are not a member of this group.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.expense = expense
            contribution.user = request.user
            contribution.save()
            messages.success(request, f'Your contribution of {expense.currency} {contribution.amount} has been recorded!')
        else:
            messages.error(request, 'Please enter a valid amount.')

    return redirect('expenses:detail', pk=expense.pk)


@login_required
def contribution_delete(request, pk):
    """A member can delete ONLY their own contribution."""
    contribution = get_object_or_404(Contribution.objects.select_related('expense'), pk=pk)
    expense = contribution.expense

    # Only the contributor themselves can delete it
    if contribution.user != request.user:
        messages.error(request, "You can only delete your own contributions.")
        return redirect('expenses:detail', pk=expense.pk)

    if request.method == 'POST':
        contribution.delete()
        messages.success(request, 'Your contribution has been removed.')

    return redirect('expenses:detail', pk=expense.pk)


@login_required
@require_POST
def scan_receipt(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not _is_group_admin(request.user, group):
        return JsonResponse({'success': False, 'error': 'Only admins can scan receipts'}, status=403)
        
    if 'receipt' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
        
    receipt_file = request.FILES['receipt']
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        for chunk in receipt_file.chunks():
            temp_file.write(chunk)
        temp_path = temp_file.name
        
    try:
        ocr_result = extract_expense_from_receipt(temp_path)
        return JsonResponse(ocr_result)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
