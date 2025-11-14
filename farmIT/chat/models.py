from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """Customer ↔ Farmer conversation, optionally tied to a specific product."""

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_farmer",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_customer",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_message_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["farmer", "customer", "product"],
                name="unique_customer_farmer_product_conversation",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        base = f"{self.customer} ↔ {self.farmer}"
        if self.product_id:
            return f"{base} ({self.product})"
        return base


class Message(models.Model):
    """Individual message within a conversation."""

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Message<{self.sender} -> {self.conversation_id}>"


