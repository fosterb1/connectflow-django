from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Ticket, TicketMessage
from .forms import TicketForm, TicketMessageForm

@login_required
def ticket_list(request):
    """List tickets for the current user."""
    tickets = Ticket.objects.filter(requester=request.user)
    return render(request, 'support/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        message_form = TicketMessageForm(request.POST, request.FILES)
        
        if form.is_valid() and message_form.is_valid():
            ticket = form.save(commit=False)
            ticket.requester = request.user
            ticket.save() # This triggers the priority auto-detection in save() logic
            
            # Create initial message
            message = message_form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            
            messages.success(request, "Support ticket created successfully.")
            return redirect('support:ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()
        message_form = TicketMessageForm()
    
    return render(request, 'support/ticket_create.html', {
        'form': form,
        'message_form': message_form
    })

@login_required
def chatbot(request):
    """Render the AI Chatbot interface."""
    return render(request, 'support/chatbot.html')

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Access control: requester or admin
    if ticket.requester != request.user and not request.user.is_admin:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect('support:ticket_list')
    
    if request.method == 'POST':
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            
            # Update ticket status if needed (e.g., if user replies, move from AWAITING_USER to OPEN)
            if request.user == ticket.requester and ticket.status == Ticket.Status.AWAITING_USER:
                ticket.status = Ticket.Status.IN_PROGRESS
                ticket.save()
                
            messages.success(request, "Reply sent.")
            return redirect('support:ticket_detail', pk=pk)
    else:
        form = TicketMessageForm()
        
    messages_list = ticket.messages.all()
    
    return render(request, 'support/ticket_detail.html', {
        'ticket': ticket,
        'messages': messages_list,
        'form': form
    })
