from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import Group, GroupMember, Invitation
from .forms import GroupForm, InviteMemberForm
from expenses.models import Expense


@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                group = form.save(commit=False)
                group.created_by = request.user
                group.save()
                # Creator becomes an admin member automatically
                GroupMember.objects.create(
                    user=request.user,
                    group=group,
                    role='admin'
                )
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('groups:detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'groups/group_form.html', {'form': form, 'action': 'Create'})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    # Ensure user is a member
    if not GroupMember.objects.filter(user=request.user, group=group).exists():
        messages.error(request, "You don't have access to this group.")
        return redirect('dashboard')
    
    members = group.group_members.select_related('user').all()
    expenses = group.expenses.select_related('paid_by').order_by('-date')[:10]
    invitations = group.invitations.filter(status='pending')
    
    # Check if current user is admin
    is_admin = members.filter(user=request.user, role='admin').exists()

    context = {
        'group': group,
        'members': members,
        'expenses': expenses,
        'invitations': invitations,
        'is_admin': is_admin,
    }
    return render(request, 'groups/group_detail.html', context)


@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    # Only admin can edit
    if not GroupMember.objects.filter(user=request.user, group=group, role='admin').exists():
        messages.error(request, "Only group admins can edit the group.")
        return redirect('groups:detail', pk=group.pk)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully.')
            return redirect('groups:detail', pk=group.pk)
    else:
        form = GroupForm(instance=group)
        
    return render(request, 'groups/group_form.html', {'form': form, 'action': 'Edit', 'group': group})


@login_required
def invite_member(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    if not GroupMember.objects.filter(user=request.user, group=group, role='admin').exists():
        messages.error(request, "Only group admins can invite members.")
        return redirect('groups:detail', pk=group.pk)

    if request.method == 'POST':
        form = InviteMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if already a member
            if group.members.filter(email=email).exists():
                messages.warning(request, f'User with email {email} is already in the group.')
            elif Invitation.objects.filter(group=group, email=email, status='pending').exists():
                messages.warning(request, f'An invitation is already pending for {email}.')
            else:
                Invitation.objects.create(
                    group=group,
                    email=email,
                    invited_by=request.user
                )
                messages.success(request, f'Invitation sent to {email}.')
            return redirect('groups:detail', pk=group.pk)
    else:
        form = InviteMemberForm()
        
    return render(request, 'groups/invite_form.html', {'form': form, 'group': group})


@login_required
def remove_member(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk)
    
    # Check admin privileges
    if not GroupMember.objects.filter(user=request.user, group=group, role='admin').exists():
        messages.error(request, "Only group admins can remove members.")
        return redirect('groups:detail', pk=group.pk)
        
    member = get_object_or_404(GroupMember, group=group, user_id=user_id)
    
    if member.user == request.user:
        messages.error(request, "You cannot remove yourself this way. Use 'Leave Group' instead.")
    else:
        # Prevent removing if they have unsettled balances - simplified check for now
        member.delete()
        messages.success(request, f"{member.display_name} has been removed from the group.")
        
    return redirect('groups:detail', pk=group.pk)

@login_required
def accept_invitation(request, pk):
    invitation = get_object_or_404(Invitation, pk=pk)
    
    if request.user.email.lower() != invitation.email.lower():
        messages.error(request, "This invitation was sent to a different email address.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            with transaction.atomic():
                invitation.status = 'accepted'
                invitation.save()
                GroupMember.objects.get_or_create(
                    user=request.user,
                    group=invitation.group,
                    defaults={'role': 'member'}
                )
            messages.success(request, f"You have successfully joined {invitation.group.name}.")
        elif action == 'decline':
            invitation.status = 'declined'
            invitation.save()
            messages.info(request, f"You declined the invitation to join {invitation.group.name}.")
            
    return redirect('dashboard')


@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    # Only admin can delete
    if not GroupMember.objects.filter(user=request.user, group=group, role='admin').exists():
        messages.error(request, "Only group admins can delete the group.")
        return redirect('groups:detail', pk=group.pk)

    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Group "{group_name}" has been deleted.')
        return redirect('dashboard')
        
    return render(request, 'groups/group_confirm_delete.html', {'group': group})
