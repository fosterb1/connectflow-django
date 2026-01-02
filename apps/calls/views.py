from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
import json
import secrets

from apps.chat_channels.models import Call, CallParticipant, Channel
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
@require_POST
def initiate_call(request):
    """Initiate a new call (audio or video)."""
    try:
        data = json.loads(request.body)
        call_type = data.get('call_type', 'AUDIO')  # AUDIO or VIDEO
        channel_id = data.get('channel_id')
        user_ids = data.get('user_ids', [])  # For direct calls
        
        # Generate unique room ID
        room_id = secrets.token_urlsafe(16)
        
        # Create call
        call = Call.objects.create(
            initiator=request.user,
            call_type=call_type,
            room_id=room_id,
            status=Call.CallStatus.INITIATING
        )
        
        # If channel call
        if channel_id:
            channel = get_object_or_404(Channel, pk=channel_id)
            call.channel = channel
            call.save()
            
            # Add all channel members as participants
            for member in channel.members.all():
                CallParticipant.objects.create(
                    call=call,
                    user=member,
                    status=CallParticipant.ParticipantStatus.INVITED
                )
        else:
            # Direct call with specific users
            participants = User.objects.filter(id__in=user_ids)
            for user in participants:
                CallParticipant.objects.create(
                    call=call,
                    user=user,
                    status=CallParticipant.ParticipantStatus.INVITED
                )
            
            # Add initiator
            CallParticipant.objects.get_or_create(
                call=call,
                user=request.user,
                defaults={'status': CallParticipant.ParticipantStatus.JOINED}
            )
        
        # Update call status to ringing
        call.status = Call.CallStatus.RINGING
        call.save()
        
        return JsonResponse({
            'success': True,
            'call_id': str(call.id),
            'room_id': call.room_id
        })
    
    except Exception as e:
        import traceback
        print("Call initiation error:", traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def call_room(request, call_id):
    """Render the call room page."""
    call = get_object_or_404(Call, pk=call_id)
    
    # Check if user is participant
    if not call.participants.filter(id=request.user.id).exists():
        return redirect('chat_channels:channel_list')
    
    # Get participant record
    participant = CallParticipant.objects.get(call=call, user=request.user)
    
    # Get all participants
    participants = CallParticipant.objects.filter(call=call).select_related('user')
    
    # STUN/TURN server configuration
    ice_servers = [
        {'urls': 'stun:stun.l.google.com:19302'},
        {'urls': 'stun:stun1.l.google.com:19302'},
        {'urls': 'stun:stun2.l.google.com:19302'},
    ]
    
    context = {
        'call': call,
        'participant': participant,
        'participants': participants,
        'ice_servers': json.dumps(ice_servers),
        'is_initiator': call.initiator == request.user,
    }
    
    return render(request, 'calls/call_room.html', context)


@login_required
@require_POST
def join_call(request, call_id):
    """Join an existing call."""
    call = get_object_or_404(Call, pk=call_id)
    
    # Get or create participant
    participant, created = CallParticipant.objects.get_or_create(
        call=call,
        user=request.user,
        defaults={'status': CallParticipant.ParticipantStatus.JOINED}
    )
    
    if not created:
        participant.status = CallParticipant.ParticipantStatus.JOINED
        participant.joined_at = timezone.now()
        participant.save()
    
    # Update call status to active if not already
    if call.status == Call.CallStatus.RINGING:
        call.status = Call.CallStatus.ACTIVE
        call.started_at = timezone.now()
        call.save()
    
    return JsonResponse({
        'success': True,
        'room_id': call.room_id
    })


@login_required
@require_POST
def leave_call(request, call_id):
    """Leave a call."""
    call = get_object_or_404(Call, pk=call_id)
    
    try:
        participant = CallParticipant.objects.get(call=call, user=request.user)
        participant.status = CallParticipant.ParticipantStatus.LEFT
        participant.left_at = timezone.now()
        participant.save()
        
        # Check if all participants have left
        active_participants = CallParticipant.objects.filter(
            call=call,
            status=CallParticipant.ParticipantStatus.JOINED
        ).count()
        
        if active_participants == 0:
            call.status = Call.CallStatus.ENDED
            call.ended_at = timezone.now()
            call.save()
        
        return JsonResponse({'success': True})
    
    except CallParticipant.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not in call'}, status=400)


@login_required
@require_POST
def end_call(request, call_id):
    """End a call (initiator only)."""
    call = get_object_or_404(Call, pk=call_id)
    
    # Only initiator can end call for everyone
    if call.initiator != request.user:
        return JsonResponse({'success': False, 'error': 'Only initiator can end call'}, status=403)
    
    # Update all participants
    CallParticipant.objects.filter(call=call).update(
        status=CallParticipant.ParticipantStatus.LEFT,
        left_at=timezone.now()
    )
    
    # End call
    call.status = Call.CallStatus.ENDED
    call.ended_at = timezone.now()
    call.save()
    
    return JsonResponse({'success': True})


@login_required
def call_status(request, call_id):
    """Get current call status."""
    call = get_object_or_404(Call, pk=call_id)
    
    participants = CallParticipant.objects.filter(call=call).select_related('user')
    
    return JsonResponse({
        'status': call.status,
        'call_type': call.call_type,
        'participants': [{
            'user_id': str(p.user.id),
            'username': p.user.username,
            'full_name': p.user.get_full_name(),
            'status': p.status,
            'is_audio_enabled': p.is_audio_enabled,
            'is_video_enabled': p.is_video_enabled,
            'is_screen_sharing': p.is_screen_sharing,
        } for p in participants]
    })
