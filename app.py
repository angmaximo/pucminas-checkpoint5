import os
from flask import Flask, request, render_template_string, redirect, url_for, flash
from google.cloud import storage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave_secreta_para_flash_messages")

# --- CONFIGURAÇÕES DO GOOGLE CLOUD STORAGE ---
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")

def get_storage_client():
    try:
        return storage.Client()   # Cloud Run já injeta o projeto automaticamente
    except Exception as e:
        print(f"Erro ao inicializar o cliente do Google Cloud Storage: {e}")
        return None

# --- CONFIGURAÇÕES DE E-MAIL (SMTP) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")

# --- TEMPLATE HTML INTEGRADO ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Upload para Google Cloud Storage</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; line-height: 1.6; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="email"], input[type="file"] { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background-color: #4285F4; color: white; border: none; padding: 10px 15px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #3367D6; }
        .message { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h2>Upload de Imagem para Google Cloud Storage</h2>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="message {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <form action="/upload" method="POST" enctype="multipart/form-data">
        <div class="form-group">
            <label for="nome">Seu Nome:</label>
            <input type="text" id="nome" name="nome" required>
        </div>
        <div class="form-group">
            <label for="email">Seu E-mail (para confirmação):</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div class="form-group">
            <label for="imagem">Selecione a Imagem:</label>
            <input type="file" id="imagem" name="imagem" accept="image/*" required>
        </div>
        <button type="submit">Enviar Imagem</button>
    </form>
</body>
</html>
"""

def enviar_email_confirmacao(destinatario, nome_usuario, nome_arquivo):
    mensagem = MIMEMultipart()
    mensagem['From'] = EMAIL_REMETENTE
    mensagem['To'] = destinatario
    mensagem['Subject'] = "Confirmação de Upload - Google Cloud Storage"

    corpo = f"""
    Olá, {nome_usuario}!
    
    Confirmamos que o upload do seu arquivo '{nome_arquivo}' foi realizado com sucesso para o Google Cloud Storage.
    
    Obrigado!
    """
    mensagem.attach(MIMEText(corpo, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.sendmail(EMAIL_REMETENTE, destinatario, mensagem.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    storage_client = get_storage_client()
    if not storage_client:
        flash("Erro interno: Google Cloud Storage não foi inicializado.", "error")
        return redirect(url_for('index'))

    if not GCP_BUCKET_NAME:
        flash("Erro interno: variável GCP_BUCKET_NAME não definida.", "error")
        return redirect(url_for('index'))

    nome = request.form.get('nome')
    email = request.form.get('email')
    arquivo = request.files.get('imagem')

    if not arquivo or arquivo.filename == '':
        flash("Nenhum arquivo selecionado.", "error")
        return redirect(url_for('index'))

    try:
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(arquivo.filename)
        blob.upload_from_string(arquivo.read(), content_type=arquivo.content_type)

        try:
            email_enviado = enviar_email_confirmacao(email, nome, arquivo.filename)
            if email_enviado:
                flash(f"Sucesso! Imagem salva no Google Cloud Storage e e-mail enviado para {email}.", "success")
            else:
                flash(f"Imagem salva no Google Cloud Storage! (Nota: envio de e-mail falhou).", "success")
        except Exception:
            flash(f"Imagem salva no Google Cloud Storage! (E-mail não enviado).", "success")

    except Exception as e:
        flash(f"Erro ao salvar no Google Cloud Storage: {str(e)}", "error")

    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
