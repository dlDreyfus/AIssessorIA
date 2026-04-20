from openai import OpenAI
from decouple import config
from .models import Message
import PyPDF2
import docx

# Inicializa o cliente da OpenAI buscando a chave do arquivo .env
client = OpenAI(api_key=config("OPENAI_API_KEY"))


def processar_mensagem_chat(conversation, user_content, arquivo=None):
    """
    Salva a mensagem do usuário, consulta a OpenAI mantendo o contexto
    da conversa e salva a resposta do assistente.
    """
    # Verifica se há um arquivo e tenta extrair seu conteúdo de texto
    if arquivo:
        nome_arquivo = arquivo.name.lower()
        try:
            if nome_arquivo.endswith('.pdf'):
                # Extrai texto de arquivos PDF
                leitor_pdf = PyPDF2.PdfReader(arquivo)
                conteudo = "\n".join([pagina.extract_text() for pagina in leitor_pdf.pages if pagina.extract_text()])
            elif nome_arquivo.endswith('.docx'):
                # Extrai texto de arquivos do Word
                documento_word = docx.Document(arquivo)
                conteudo = "\n".join([paragrafo.text for paragrafo in documento_word.paragraphs])
            else:
                # Tenta decodificar o arquivo como texto puro (ex: .txt, .csv, .json, .md)
                conteudo = arquivo.read().decode('utf-8')
                
            user_content = f"{user_content}\n\n[Conteúdo do Arquivo '{arquivo.name}']:\n{conteudo}"
        except UnicodeDecodeError:
            # Se for outro formato binário não suportado (ex: .xlsx, .jpg)
            user_content = f"{user_content}\n\n[Arquivo '{arquivo.name}' anexado. Aviso do sistema: Este é um arquivo binário não suportado e seu conteúdo nativo não pôde ser extraído como texto.]"
        except Exception as e:
            # Captura erros de leitura de PDF/Word (arquivos corrompidos, protegidos por senha, etc.)
            user_content = f"{user_content}\n\n[Arquivo '{arquivo.name}' anexado. Aviso do sistema: Erro ao tentar processar o arquivo - {str(e)}]"

    # 1. Salva a mensagem do usuário no banco de dados
    Message.objects.create(conversation=conversation, role="user", content=user_content)

    # 2. Recupera o histórico da conversa ordenado do mais antigo ao mais novo
    # Isso é essencial para o ChatGPT "lembrar" do que foi dito antes
    historico_mensagens = conversation.messages.all().order_by("created_at")

    # 3. Define a resposta padrão temporária (App em desenvolvimento)
    conteudo_assistente = "Este aplicativo ainda está em desenvolvimento"

    # 4. Salva a resposta do assistente no banco
    Message.objects.create(
        conversation=conversation, role="assistant", content=conteudo_assistente
    )

    return conteudo_assistente
