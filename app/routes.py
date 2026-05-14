from main import app, get_db
from flask import render_template, request, jsonify, redirect, url_for
from flask_bcrypt import Bcrypt
from services.auth_service import gerar_token_recuperacao, validar_token
from services.email_service import enviar_email_recuperacao
import os
from dotenv import load_dotenv
import jwt
import datetime
from functools import wraps
import hashlib
from app.crypto import *
import base64

bcrypt = Bcrypt(app)

load_dotenv()

# Decorador para proteger rotas que requerem autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        SECRET_KEY = os.getenv("SECRET_KEY")
        
        if not token or not SECRET_KEY:
            return render_template("login.html")
        
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return render_template("login.html")
        
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("recuperar_password/forgot_password.html")

@app.route("/reset-password")
def reset_password_page():
    return render_template("recuperar_password/reset_password.html")

@app.route("/auth/request-reset", methods=["POST"])
def request_reset():
    data = request.get_json()
    email = data.get("email")

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()

    if not user:
        return jsonify({"success": False, "error": "Email não encontrado"}), 404

    from model.User import User
    user_obj = User(user[0], user[1], user[2], user[3])

    token = gerar_token_recuperacao(user_obj)

    # guardar token na BD
    cursor.execute("""
        UPDATE user
        SET reset_token = ?, reset_token_expira = ?
        WHERE email = ?
    """, (user_obj.reset_token, user_obj.reset_token_expira, email))
    db.commit()

    enviar_email_recuperacao(user_obj, token)

    return jsonify({"success": True, "message": "Email enviado!"})

@app.route("/auth/reset-password", methods=["POST"])
def reset_password_route():
    data = request.get_json()
    token = data.get("token")
    nova_password = data.get("password")

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT * FROM user WHERE reset_token = ?", (token,)).fetchone()

    if not user:
        return jsonify({"success": False, "error": "Token inválido"}), 400

    from model.User import User
    user_obj = User(user[0], user[1], user[2], user[3])
    user_obj.reset_token = user[4]
    # Converter string da BD para objeto datetime
    user_obj.reset_token_expira = datetime.datetime.fromisoformat(user[5])

    if not validar_token(user_obj, token):
        return jsonify({"success": False, "error": "Token expirado"}), 400

    # hash da nova password
    pw_hash = bcrypt.generate_password_hash(nova_password, 10)

    cursor.execute("""
        UPDATE user
        SET password = ?, reset_token = NULL, reset_token_expira = NULL
        WHERE email = ?
    """, (pw_hash, user_obj.email))
    db.commit()

    return jsonify({"success": True, "message": "Password atualizada!"})

@app.route("/register", methods=["GET"])
def register():
    return render_template("signup.html")

@app.route("/index")
@login_required
def index():
    return render_template("base.html")

@app.route("/deposit")
@login_required
def deposit():
    return render_template("new_message.html")

@app.route("/open_vault")
@login_required
def open_vault():
    return render_template("open_vault.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/auth/signout")
@login_required
def signout():
    response = redirect(url_for('login'))

    response.delete_cookie('token')

    return response

@app.route("/auth/registerUser", methods=["POST"])
def registerUser():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"success": False, "error": "Preenche todos os campos"}), 400

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
    if user:
        return jsonify({"success": False, "error": "Email já registado"}), 409

    #password hashing 10-number of rounds for salt
    pw_hash = bcrypt.generate_password_hash(password, 10)

    cursor.execute("""
        INSERT INTO user (username, email, password)
        VALUES (?, ?, ?)
    """, (username, email, pw_hash))
    db.commit()

    return jsonify({"success": True, "message": "Utilizador registado com sucesso!"}), 201

@app.route("/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"success": False, "error": "Missing email or password"}), 400
    
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()

    if not user:
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    stored_hash = user[3]

    if not bcrypt.check_password_hash(stored_hash, password):
        return jsonify({"success": False, "error": "Incorrect email or password"}), 401

    
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        return jsonify({"success": False, "error": "Server configuration error"}), 500
    
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    response = jsonify({"success": True, "message": "Login successful!"})

    response.set_cookie('token', token, httponly=True)

    return response, 200
    
@app.route("/", methods=["GET"])
def check_jwt():
    token = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    if not token or not SECRET_KEY:
        return render_template("home.html")

    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return render_template("base.html")
    except jwt.InvalidTokenError:
        return render_template("home.html")


@app.route("/auth/check", methods=["GET"])
def auth_check():
    token = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not token or not SECRET_KEY:
        return jsonify({"isLoggedIn": False})

    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"isLoggedIn": True})
    except jwt.InvalidTokenError:
        return jsonify({"isLoggedIn": False})

@app.after_request
def add_header(response):
    # impede o browser de voltar a uma pagina quando o acesso expirar
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

#criar cofre com mensagem        
@app.route("/message/deposit", methods=["POST"])
@login_required
def create_newMessage():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Dados não recebidos"}), 400

    title = data.get('title')
    message = data.get('message')
    method = data.get('method')
    
    alg_simetrico = data.get('algSim_bits')           
    key_source = data.get('symmetric_key_source')     
    password = data.get('password')                  

    rsa_bits = data.get('rsa_bits')                  
    rsa_key_type = data.get('rsa_key_type')           

    hmac_hash = data.get('hmac_hash')   
    sig_hash = data.get('sig_hash')

    if not message:
        return jsonify({"success": False, "error": "A mensagem nao pode estar vazia"}), 400

    # buscar o utilizador pelo token
    token = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not token or not SECRET_KEY:
        return jsonify({"success": False, "error": "Autenticação necessária"}), 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "Token inválido"}), 401

    email = decoded.get("email")

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"success": False, "error": "Utilizador não encontrado"}), 404

    utilizador_id = user[0]

    # assinar o texto limpo (ainda sem cifrar, mandamos a mensagem original)
    assDgtl = sign_digitally(sig_hash, message)
    # converter assinatura para base64 para armazenar como texto
    assinatura_b64 = base64.b64encode(assDgtl).decode()

    cryptogram = None
    private_key_data = None
    private_key_message = None

    if method == "rsa":
        try:
            rsa_bits = int(rsa_bits)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Tamanho RSA invalido"}), 400

        public_key, private_key = pk_user(utilizador_id, rsa_bits, db)
        if not public_key:
            return jsonify({"success": False, "error": "Erro ao obter chave pública"}), 500
        
        if private_key is None:
            private_key_message = "Espero que nao tenha perdido a sua chave privada.😉"
        else:
            private_key_data = private_key.decode("utf-8")
        
        cryptogram = encrypt_message_rsa(message, public_key)
    elif method == "password":
        return jsonify({"success": False, "error": "Password encryption not yet implemented"}), 501
    
    elif method == "random-key":
        return jsonify({"success": False, "error": "Random key encryption not yet implemented"}), 501
    
    else:
        return jsonify({"success": False, "error": "Invalid encryption method"}), 400

    if cryptogram is None:
        return jsonify({"success": False, "error": "Failed to encrypt message"}), 500

    hmac_auth = HMAC_authentication(hmac_hash, cryptogram.encode() if isinstance(cryptogram, str) else cryptogram)

    cursor.execute(
        "INSERT INTO mensagem (titulo, conteudoCifrado) VALUES (?, ?)",
        (title, cryptogram)
    )
    db.commit()

    mensagem_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO cofre (codigoDeAutenticacao, assinaturaDigital, tipoDeCifra, hmacHash, sigHash,utilizador_id, mensagem_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (hmac_auth, assinatura_b64, method, hmac_hash, sig_hash, utilizador_id, mensagem_id)
    )
    db.commit()

    return jsonify({
        "success": True,
        "message": "Mensagem guardada com sucesso!",
        "mensagem_id": mensagem_id,
        "private_key": private_key_data,
        "private_key_message": private_key_message
    }), 201

@app.route("/message/decrypt", methods=["GET"])
@login_required
def decrypt_message_route():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Dados não recebidos"}), 400
    
    cofre_id = data.get("mensagem_id")
    secret = data.get("secret")

    if not cofre_id or not secret:
        return jsonify({"success": False, "error": "ID da mensagem e segredo são necessários"}), 400

    token = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not token or not SECRET_KEY:
        return jsonify({"success": False, "error": "Autenticação necessária"}), 401
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "Token inválido"}), 401
    
    email = decoded.get("email")

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"success": False, "error": "Utilizador não encontrado"}), 404 

    resultado = cursor.execute("""
        SELECT c.tipoDeCifra, c.mensagem_id
        FROM cofre c
        WHERE c.id = ?
    """, (cofre_id,)).fetchone()

    if resultado:
        method, mensagem_id = resultado

        conteudo_cifrado = cursor.execute("""
            SELECT m.conteudoCifrado
            FROM mensagem m
            WHERE m.id = ?
        """, (mensagem_id,)).fetchone()

    if conteudo_cifrado:
        conteudo_cifrado = conteudo_cifrado[0]


    if method == "rsa":
        mensagem = decrypt_message_rsa(secret, conteudo_cifrado)
