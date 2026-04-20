from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("", views.chat_interface, name="interface"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path(
        "api/send/<uuid:conversation_id>/",
        views.enviar_mensagem_api,
        name="enviar_mensagem",
    ),
]
