from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from products.models import Product, Farm

from farmIT.throttling import check_throttle

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
        .only(
            "id",
            "farmer__id",
            "farmer__username",
            "customer__id",
            "customer__username",
            "product__id",
            "product__product_name",
            "last_message_at",
            "created_at",
        )
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
        throttle = check_throttle(f"chat:send:{request.user.id}:{conversation.pk}", limit=60, window_seconds=60)
        if not throttle.allowed:
            # Avoid leaking operational details; keep response generic.
            return HttpResponse("Too many messages, please slow down.", status=429)

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
    throttle = check_throttle(f"chat:start_product:{request.user.id}", limit=20, window_seconds=60)
    if not throttle.allowed:
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

    throttle = check_throttle(f"chat:start_farm:{request.user.id}", limit=20, window_seconds=60)
    if not throttle.allowed:
        return HttpResponse("Too many new conversations, please slow down.", status=429)

    conversation, _created = Conversation.objects.get_or_create(
        farmer=farm.farmer,
        customer=request.user,
        product=None,
        defaults={"last_message_at": timezone.now()},
    )
    return redirect("chat_conversation_detail", pk=conversation.pk)


@login_required
def get_messages_json(request: HttpRequest, pk: int) -> JsonResponse:
    """JSON endpoint to fetch messages for auto-refresh."""
    throttle = check_throttle(f"chat:poll:{request.user.id}:{pk}", limit=120, window_seconds=60)
    if not throttle.allowed:
        return JsonResponse({"error": "Too many requests, slow down."}, status=429)

    conversation = get_object_or_404(
        Conversation.objects.filter(
            Q(farmer=request.user) | Q(customer=request.user)
        ),
        pk=pk,
    )

    # Get last message ID from query param to only fetch new messages
    last_id = request.GET.get("last_id", 0)
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0

    messages_qs = conversation.messages.filter(id__gt=last_id).select_related("sender").order_by("created_at")

    # Mark new messages from the other party as read
    messages_qs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    messages_data = []
    for msg in messages_qs:
        messages_data.append({
            "id": msg.id,
            "body": msg.body,
            "sender_id": msg.sender_id,
            "sender_username": msg.sender.username,
            "created_at": msg.created_at.strftime("%b %d, %H:%M"),
            "is_own": msg.sender_id == request.user.id,
        })

    return JsonResponse({"messages": messages_data})


