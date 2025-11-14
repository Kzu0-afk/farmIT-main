from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from products.models import Product, Farm

from .forms import MessageForm
from .models import Conversation, Message


@login_required
def inbox(request: HttpRequest) -> HttpResponse:
    """Simple message center showing all conversations for the current user."""
    conversations = (
        Conversation.objects.filter(
            Q(farmer=request.user) | Q(customer=request.user)
        )
        .select_related("farmer", "customer", "product")
        .order_by("-last_message_at", "-created_at")
    )

    return render(
        request,
        "chat/inbox.html",
        {
            "conversations": conversations,
        },
    )


@login_required
def conversation_detail(request: HttpRequest, pk: int) -> HttpResponse:
    conversation = get_object_or_404(
        Conversation.objects.filter(
            Q(farmer=request.user) | Q(customer=request.user)
        ),
        pk=pk,
    )

    messages_qs = conversation.messages.select_related("sender").order_by("created_at")

    # Mark messages from the other party as read.
    messages_qs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"].strip()
            if body:
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    body=body,
                )
                conversation.last_message_at = timezone.now()
                conversation.save(update_fields=["last_message_at"])
            return redirect("chat_conversation_detail", pk=conversation.pk)
    else:
        form = MessageForm()

    return render(
        request,
        "chat/conversation_detail.html",
        {
            "conversation": conversation,
            "messages": messages_qs,
            "form": form,
        },
    )


@login_required
def start_conversation_product(request: HttpRequest, product_id: int) -> HttpResponse:
    """Customer-initiated conversation from a product detail page."""
    if request.method != "POST":
        return redirect("product_detail", pk=product_id)

    if not getattr(request.user, "is_customer", False):
        return HttpResponseForbidden("Only customer accounts can start conversations.")

    product = get_object_or_404(Product, pk=product_id, is_approved=True)

    if product.farmer_id == request.user.id:
        return HttpResponseForbidden("You cannot start a chat with your own listing.")

    # Lightweight per-user throttling on conversation creation.
    window_start = timezone.now() - timedelta(minutes=1)
    recent_count = Conversation.objects.filter(
        customer=request.user,
        created_at__gte=window_start,
    ).count()
    if recent_count > 20:
        return HttpResponse("Too many new conversations, please slow down.", status=429)

    conversation, _created = Conversation.objects.get_or_create(
        farmer=product.farmer,
        customer=request.user,
        product=product,
        defaults={"last_message_at": timezone.now()},
    )
    return redirect("chat_conversation_detail", pk=conversation.pk)


@login_required
def start_conversation_farm(request: HttpRequest, slug: str) -> HttpResponse:
    """Customer-initiated conversation from a farm page."""
    if request.method != "POST":
        return redirect("farm_detail", slug=slug)

    if not getattr(request.user, "is_customer", False):
        return HttpResponseForbidden("Only customer accounts can start conversations.")

    farm = get_object_or_404(Farm, slug=slug)

    if farm.farmer_id == request.user.id:
        return HttpResponseForbidden("You cannot start a chat with your own farm.")

    window_start = timezone.now() - timedelta(minutes=1)
    recent_count = Conversation.objects.filter(
        customer=request.user,
        created_at__gte=window_start,
    ).count()
    if recent_count > 20:
        return HttpResponse("Too many new conversations, please slow down.", status=429)

    conversation, _created = Conversation.objects.get_or_create(
        farmer=farm.farmer,
        customer=request.user,
        product=None,
        defaults={"last_message_at": timezone.now()},
    )
    return redirect("chat_conversation_detail", pk=conversation.pk)


