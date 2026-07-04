from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Settlement
from .forms import SettlementForm
from groups.models import Group, GroupMember


def _is_group_member(user, group):
    return GroupMember.objects.filter(user=user, group=group).exists()


@login_required
def settlement_list(request, group_id):
    """View all settlements for a specific group."""
    group = get_object_or_404(Group, pk=group_id)
    
    if not _is_group_member(request.user, group):
        messages.error(request, "You don't have access to this group's settlements.")
        return redirect('dashboard')
        
    settlements = group.settlements.select_related('from_user', 'to_user').all()
    
    return render(request, 'settlements/settlement_list.html', {
        'group': group,
        'settlements': settlements
    })


@login_required
def settlement_create(request, group_id):
    """Record a new payment to another group member."""
    group = get_object_or_404(Group, pk=group_id)
    
    if not _is_group_member(request.user, group):
        messages.error(request, "You don't have access to this group.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SettlementForm(request.POST, group=group, user=request.user)
        if form.is_valid():
            settlement = form.save(commit=False)
            settlement.group = group
            settlement.from_user = request.user
            settlement.save()
            messages.success(request, f'Payment of {settlement.currency} {settlement.amount} recorded successfully!')
            return redirect('settlements:list', group_id=group.pk)
    else:
        initial_data = {}
        if 'to_user' in request.GET:
            initial_data['to_user'] = request.GET.get('to_user')
        if 'amount' in request.GET:
            initial_data['amount'] = request.GET.get('amount')
            
        form = SettlementForm(group=group, user=request.user, initial=initial_data)
        
    return render(request, 'settlements/settlement_form.html', {
        'form': form,
        'group': group
    })


@login_required
def settlement_complete(request, pk):
    """Mark a settlement as completed (only to_user can do this)."""
    settlement = get_object_or_404(Settlement.objects.select_related('group', 'to_user'), pk=pk)
    
    # Only the person receiving the money can confirm it's completed
    if request.user != settlement.to_user:
        messages.error(request, "Only the recipient can confirm this payment.")
        return redirect('settlements:list', group_id=settlement.group.pk)
        
    if request.method == 'POST':
        settlement.is_completed = True
        from django.utils import timezone
        settlement.completed_at = timezone.now()
        settlement.save()
        messages.success(request, f"Payment from {settlement.from_user.username} has been confirmed as received!")
        
    return redirect('settlements:list', group_id=settlement.group.pk)
