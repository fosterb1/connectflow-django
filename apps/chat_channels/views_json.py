from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Channel, Message
import json

@login_required
def channels_for_forward(request):
    """Simple JSON endpoint for forward modal - bypasses DRF"""
    try:
        # Get user's channels
        channels = Channel.objects.filter(
            members=request.user,
            is_archived=False
        ).values('id', 'name', 'channel_type', 'description')
        
        # Convert to list and add member count
        channel_list = []
        for ch in channels:
            channel_list.append({
                'id': str(ch['id']),
                'name': ch['name'],
                'channel_type': ch['channel_type'],
                'description': ch.get('description', ''),
                'member_count': 2  # Simplified for now
            })
        
        return JsonResponse(channel_list, safe=False)
    except Exception as e:
        # Return error as JSON
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to load channels'
        }, status=500)

@login_required
@require_POST
def forward_message(request):
    """Simple endpoint to forward a message"""
    try:
        data = json.loads(request.body)
        
        target_channel_id = data.get('channel')
        content = data.get('content', '')
        forwarded_from_id = data.get('forwarded_from')
        
        # Validate
        if not target_channel_id or not content:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get target channel
        target_channel = Channel.objects.get(id=target_channel_id)
        
        # Check user is member
        if not target_channel.members.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'Not a member of target channel'}, status=403)
        
        # Get original message if provided
        forwarded_from = None
        if forwarded_from_id:
            try:
                forwarded_from = Message.objects.get(id=forwarded_from_id)
            except Message.DoesNotExist:
                pass
        
        # Create forwarded message
        message = Message.objects.create(
            channel=target_channel,
            sender=request.user,
            content=content,
            forwarded_from=forwarded_from
        )
        
        return JsonResponse({
            'success': True,
            'message_id': str(message.id),
            'channel_id': str(target_channel.id)
        })
        
    except Channel.DoesNotExist:
        return JsonResponse({'error': 'Channel not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

