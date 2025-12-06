from django.urls import path

from . import views


urlpatterns = [
    path("", views.inbox, name="chat_inbox"),
    path("conversations/<int:pk>/", views.conversation_detail, name="chat_conversation_detail"),
    path("conversations/<int:pk>/messages.json", views.get_messages_json, name="chat_messages_json"),
    path("start/product/<int:product_id>/", views.start_conversation_product, name="chat_start_product"),
    path("start/farm/<slug:slug>/", views.start_conversation_farm, name="chat_start_farm"),
]


