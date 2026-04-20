import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Conversation
from .services import processar_mensagem_chat


def chat_interface(request):
    """Renderiza a tela principal do Chat (HTML)"""
    conversation = None
    if request.user.is_authenticated:
        # Busca a última conversa exclusiva do usuário logado
        conversation = Conversation.objects.filter(user=request.user).order_by("-updated_at").first()
        # Melhora de UX: Auto-cria uma conversa se o usuário for novo e não tiver nenhuma
        if not conversation:
            conversation = Conversation.objects.create(user=request.user, title="Nova Conversa")

    return render(request, "chat/index.html", {"conversation": conversation})

@require_POST
def login_view(request):
    u = request.POST.get('username')
    p = request.POST.get('password')
    user = authenticate(request, username=u, password=p)
    if user is not None:
        login(request, user)
    else:
        messages.error(request, "Acesso Negado: Credenciais inválidas.")
    return redirect('chat:interface')

@require_POST
def register_view(request):
    u = request.POST.get('username')
    p = request.POST.get('password')
    p_confirm = request.POST.get('password_confirm')
    if p != p_confirm:
        messages.error(request, "Erro: As senhas não coincidem.")
    elif User.objects.filter(username=u).exists():
        messages.error(request, "Erro: Este usuário já existe no sistema.")
    else:
        user = User.objects.create_user(username=u, password=p)
        login(request, user)
    return redirect('chat:interface')

def logout_view(request):
    logout(request)
    return redirect('chat:interface')

# Usamos csrf_exempt temporariamente para facilitar os testes da API via JavaScript/Postman
# Em produção, usaremos o Token CSRF adequadamente no frontend
@csrf_exempt
@require_POST
def enviar_mensagem_api(request, conversation_id):
    """Endpoint de API para receber mensagens assincronamente via JavaScript Fetch"""
    try:
        arquivo = None
        content_type = request.META.get('CONTENT_TYPE', '')
        
        # Identifica se a requisição trouxe arquivos (FormData) ou se é um JSON normal
        if content_type.startswith('multipart/form-data'):
            mensagem_usuario = request.POST.get("message", "")
            arquivo = request.FILES.get("file")
        else:
            try:
                dados = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                dados = {}
            mensagem_usuario = dados.get("message", "")

        conversa = get_object_or_404(Conversation, id=conversation_id)

        resposta_ia = processar_mensagem_chat(conversa, mensagem_usuario, arquivo)

        return JsonResponse({"reply": resposta_ia, "status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e), "status": "error"}, status=500)
