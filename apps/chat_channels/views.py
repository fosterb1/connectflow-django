from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Channel, Message, MessageReaction
from .forms import ChannelForm, MessageForm


@login_required
def channel_list(request):
    """List all channels user has access to."""
    user = request.user
    
    if not user.organization:
        messages.warning(request, 'You are not assigned to any organization.')
        return redirect('accounts:dashboard')
    
    # Get channels user can access
    channels = Channel.objects.filter(
        organization=user.organization,
        is_archived=False
    ).select_related('department', 'team', 'created_by').prefetch_related('members')
    
    # Filter by type
    official_channels = channels.filter(channel_type=Channel.ChannelType.OFFICIAL)
    department_channels = channels.filter(channel_type=Channel.ChannelType.DEPARTMENT)
    team_channels = channels.filter(channel_type=Channel.ChannelType.TEAM)
    project_channels = channels.filter(channel_type=Channel.ChannelType.PROJECT)
    private_channels = channels.filter(channel_type=Channel.ChannelType.PRIVATE, members=user)
    
    context = {
        'official_channels': official_channels,
        'department_channels': department_channels,
        'team_channels': team_channels,
        'project_channels': project_channels,
        'private_channels': private_channels,
        'can_create': user.is_admin or user.is_manager
    }
    return render(request, 'chat_channels/channel_list.html', context)


@login_required
def channel_create(request):
    """Create a new channel."""
    user = request.user
    
    if not (user.is_admin or user.is_manager):
        messages.error(request, 'You do not have permission to create channels.')
        return redirect('chat_channels:channel_list')
    
    if request.method == 'POST':
        form = ChannelForm(request.POST, organization=user.organization)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.organization = user.organization
            channel.created_by = user
            channel.save()
            form.save_m2m()
            
            # Add creator as member
            channel.members.add(user)
            
            messages.success(request, f'Channel "#{channel.name}" created successfully!')
            return redirect('chat_channels:channel_detail', pk=channel.pk)
    else:
        form = ChannelForm(organization=user.organization)
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'chat_channels/channel_form.html', context)


@login_required
def channel_detail(request, pk):
    """View channel details and messages."""
    user = request.user
    channel = get_object_or_404(
        Channel, 
        pk=pk, 
        organization=user.organization
    )
    
    # Check if user can view this channel
    if not channel.can_user_view(user):
        messages.error(request, 'You do not have permission to view this channel.')
        return redirect('chat_channels:channel_list')
    
    # Get messages (excluding deleted and replies - they'll be shown with parent)
    channel_messages = Message.objects.filter(
        channel=channel,
        is_deleted=False,
        parent_message__isnull=True
    ).select_related('sender').prefetch_related('reactions', 'replies').order_by('created_at')
    
    # Handle message posting
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.channel = channel
            message.sender = user
            message.save()
            return redirect('chat_channels:channel_detail', pk=pk)
    else:
        form = MessageForm()
    
    context = {
        'channel': channel,
        'messages': channel_messages,
        'form': form,
        'can_edit': user.is_admin or channel.created_by == user,
        'is_member': user in channel.members.all(),
        'can_post': channel.can_user_post(user) if hasattr(channel, 'can_user_post') else user in channel.members.all()
    }
    return render(request, 'chat_channels/channel_detail.html', context)


@login_required
def channel_edit(request, pk):
    """Edit a channel."""
    user = request.user
    channel = get_object_or_404(
        Channel, 
        pk=pk, 
        organization=user.organization
    )
    
    if not (user.is_admin or channel.created_by == user):
        messages.error(request, 'You do not have permission to edit this channel.')
        return redirect('chat_channels:channel_detail', pk=pk)
    
    if request.method == 'POST':
        form = ChannelForm(request.POST, instance=channel, organization=user.organization)
        if form.is_valid():
            form.save()
            messages.success(request, f'Channel "#{channel.name}" updated successfully!')
            return redirect('chat_channels:channel_detail', pk=pk)
    else:
        form = ChannelForm(instance=channel, organization=user.organization)
    
    context = {'form': form, 'action': 'Edit', 'channel': channel}
    return render(request, 'chat_channels/channel_form.html', context)


@login_required
def channel_delete(request, pk):
    """Delete a channel."""
    user = request.user
    channel = get_object_or_404(
        Channel, 
        pk=pk, 
        organization=user.organization
    )
    
    if not user.is_admin:
        messages.error(request, 'Only admins can delete channels.')
        return redirect('chat_channels:channel_detail', pk=pk)
    
    if request.method == 'POST':
        channel_name = channel.name
        channel.delete()
        messages.success(request, f'Channel "#{channel_name}" deleted successfully!')
        return redirect('chat_channels:channel_list')
    
    context = {'channel': channel}
    return render(request, 'chat_channels/channel_confirm_delete.html', context)


@login_required
@require_POST
def message_delete(request, pk):
    """Delete a message (soft delete)."""
    user = request.user
    message = get_object_or_404(Message, pk=pk)
    
    # Only sender or admin can delete
    if message.sender == user or user.is_admin:
        message.is_deleted = True
        message.content = "[Message deleted]"
        message.save()
    
    return redirect('chat_channels:channel_detail', pk=message.channel.pk)


@login_required
@require_POST
def message_react(request, pk):
    """Add or remove a reaction to a message."""
    user = request.user
    message = get_object_or_404(Message, pk=pk)
    emoji = request.POST.get('emoji', '👍')
    
    # Check if reaction already exists
    reaction, created = MessageReaction.objects.get_or_create(
        message=message,
        user=user,
        emoji=emoji
    )
    
    if not created:
        # Remove reaction if it already exists
        reaction.delete()
        action = 'removed'
    else:
        action = 'added'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for AJAX requests
        return JsonResponse({
            'success': True,
            'action': action,
            'reaction_summary': message.reaction_summary
        })
    
    return redirect('chat_channels:channel_detail', pk=message.channel.pk)
