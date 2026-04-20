from openai import OpenAI
from decouple import config
from .models import Message

# Inicializa o cliente da OpenAI buscando a chave do arquivo .env
client = OpenAI(api_key=config("OPENAI_API_KEY"))


def processar_mensagem_chat(conversation, user_content):
    """
    Salva a mensagem do usuário, consulta a OpenAI mantendo o contexto
    da conversa e salva a resposta do assistente.
    """
    # 1. Salva a mensagem do usuário no banco de dados
    Message.objects.create(conversation=conversation, role="user", content=user_content)

    # 2. Recupera o histórico da conversa ordenado do mais antigo ao mais novo
    # Isso é essencial para o ChatGPT "lembrar" do que foi dito antes
    historico_mensagens = conversation.messages.all().order_by("created_at")

    # 3. Formata as mensagens para o padrão exigido pela API da OpenAI
    mensagens_api = [
        {"role": "system", "content": "Você é um assistente prestativo e inteligente."}
    ]
    for msg in historico_mensagens:
        mensagens_api.append({"role": msg.role, "content": msg.content})

    # 4. Faz a requisição para a OpenAI
    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Você pode mudar para gpt-4 se preferir
        messages=mensagens_api,
        temperature=0.7,
    )

    conteudo_assistente = resposta.choices[0].message.content

    # 5. Salva a resposta do assistente no banco
    Message.objects.create(
        conversation=conversation, role="assistant", content=conteudo_assistente
    )

    return conteudo_assistente
