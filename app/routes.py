from main import app, get_db
from flask import g, render_template, request, jsonify, redirect, url_for
from flask_bcrypt import Bcrypt
from services.auth_service import (
    gerar_token_recuperacao,
    validar_token,
    gerar_delete_token,
)
from services.email_service import enviar_email_apagar_cofre, enviar_email_recuperacao
import os
from dotenv import load_dotenv
import jwt
import datetime
from functools import wraps
import hashlib
from app.crypto import *
import base64

bcrypt = Bcrypt(app)

# guarda temporariamente o segredo usado para abrir cofres com chave derivada de password
_vault_secret_cache = {}

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
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            g.current_user = decoded_token

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
        return jsonify({"success": False, "error": "Email not found"}), 404

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

    return jsonify({"success": True, "message": "Email sent!"})

@app.route("/auth/reset-password", methods=["POST"])
def reset_password_route():
    data = request.get_json()
    token = data.get("token")
    nova_password = data.get("password")

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT * FROM user WHERE reset_token = ?", (token,)).fetchone()

    if not user:
        return jsonify({"success": False, "error": "Token invalid"}), 400

    from model.User import User
    user_obj = User(user[0], user[1], user[2], user[3])
    user_obj.reset_token = user[4]
    # Converter string da BD para objeto datetime
    user_obj.reset_token_expira = datetime.datetime.fromisoformat(user[5])

    if not validar_token(user_obj, token):
        return jsonify({"success": False, "error": "Token expired"}), 400

    # hash da nova password
    pw_hash = bcrypt.generate_password_hash(nova_password, 10)

    cursor.execute("""
        UPDATE user
        SET password = ?, reset_token = NULL, reset_token_expira = NULL
        WHERE email = ?
    """, (pw_hash, user_obj.email))
    db.commit()

    return jsonify({"success": True, "message": "Password updated!"})

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

# @app.route("/open_result")
# @login_required
# def open_result():
#     return render_template("open_result.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        new_username = request.form.get("uname")
        new_email = request.form.get("email")

        old_email = g.current_user["email"]

        db = get_db()
        cursor = db.cursor()

        #Update user row on db    
        cursor.execute(
            "UPDATE user SET username = ?, email = ? WHERE email = ?",
            (new_username, new_email, old_email)
        )
        db.commit()

        SECRET_KEY = os.getenv("SECRET_KEY")
        new_payload = {
            "email": new_email,
            "username": new_username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }

        #new token to update info on profile
        new_token = jwt.encode(new_payload, SECRET_KEY, algorithm="HS256")

        response = redirect(url_for('profile'))
        response.set_cookie('token', new_token, httponly=True)

        return response

    return render_template("profile.html", user=g.current_user)

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
        return jsonify({"success": False, "error": "Fill all the fields."}), 400

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
    if user:
        return jsonify({"success": False, "error": "Email is already registered"}), 409

    #password hashing 10-number of rounds for salt
    pw_hash = bcrypt.generate_password_hash(password, 10)

    cursor.execute("""
        INSERT INTO user (username, email, password)
        VALUES (?, ?, ?)
    """, (username, email, pw_hash))
    db.commit()

    # obter id do utilizador recém-criado
    utilizador_id = cursor.lastrowid

    # gerar chaves RSA para o utilizador (armazenamos apenas a pública; devolvemos a privada ao utilizador)
    private_key_data = None
    private_key_message = None
    try:
        public_key, private_key = pk_user(utilizador_id, 2048, "no_antiga", db)
        if private_key is not None:
            private_key_data = private_key.decode("utf-8")
            private_key_message = "Keep your private key in a safe location. The server does not keep record of it."
    except Exception as e:
        # falha na geração de chaves — não impede o registo, apenas não devolve a chave
        private_key_data = None
        private_key_message = "Error generating private key in the server."

    return jsonify({
        "success": True,
        "message": "User registered with success!",
        "private_key": private_key_data,
        "private_key_message": private_key_message,
        "user_id": utilizador_id
    }), 201

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
        "username": user[1],
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
        return jsonify({"success": False, "error": "Data not received"}), 400

    title = data.get('title')
    message = data.get('message')
    method = data.get('method')
    
    type_sim = data.get('algSim_bits')           
    key_source = data.get('symmetric_key_source')     
    password = data.get('password')                  

    rsa_bits = data.get('rsa_bits')                  
    rsa_key_type = data.get('rsa_key_type')           

    hmac_hash = data.get('hmac_hash')   
    sig_hash = data.get('sig_hash')

    if not message:
        return jsonify({"success": False, "error": "The message cannot be empty"}), 400

    # buscar o utilizador pelo token
    token = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not token or not SECRET_KEY:
        return jsonify({"success": False, "error": "Authentication necessary"}), 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "Token invalid"}), 401

    email = decoded.get("email")

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    utilizador_id = user[0]

    # assinar o texto limpo (ainda sem cifrar, mandamos a mensagem original)
    assDgtl = sign_digitally(sig_hash, message)
    # converter assinatura para base64 para armazenar como texto
    assinatura_b64 = base64.b64encode(assDgtl).decode()

    cryptogram = None
    private_key_data = None
    private_key_message = None
    salt = None

    if method == "rsa":
        try:
            rsa_bits = int(rsa_bits)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "RSA size invalid"}), 400

        public_key, private_key = pk_user(utilizador_id, rsa_bits, rsa_key_type, db)
        if not public_key:
            return jsonify({"success": False, "error": "Error obtaining public key"}), 500
        
        if private_key is None:
            private_key_message = "I hope you have not lost your private key.😉"
        else:
            private_key_data = private_key.decode("utf-8")
        
        cryptogram = encrypt_message_rsa(message, public_key)
    elif method == "random-key":
        #verificar se tenho de criar uma chave nova ou usar a que o utilizador inseriu
        if key_source == 'passChosen':
            #udeixar o hmac verificar se a plaavra passe é a certa ou nao
            salt, secretKey = deriveKey(password, None)
            salt = base64.b64encode(salt).decode("utf-8")
        else:
            #gerar pass random
            secretKey = random_bytes(32)
            private_key_data = base64.b64encode(secretKey).decode("utf-8")

        #verificar qual o algoritmo simetrico
        if type_sim == 'AES-256-CBC':
            cryptogram, iv = aes256_cbc_encrypt(message, secretKey, None)
        elif type_sim == 'AES-256-CTR':
            cryptogram, iv = aes256_ctr_encrypt(message, secretKey, None)
        elif type_sim == 'ChaCha20':
            cryptogram, iv = encrypt_chacha20(message, secretKey, None)
        else:
            return jsonify({"success": False, "error": "Type of symmetric algorithm not supported"}), 501
    
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

    #só insere na base de dados a chave publica se for rsa, se for uma nova e se ela existir
    if method == 'rsa' and rsa_key_type == 'yes_nova' and public_key:
        cursor.execute(
            "INSERT INTO cofre (codigoDeAutenticacao, assinaturaDigital, tipoDeCifra, hmacHash, sigHash, utilizador_id, mensagem_id, pkRsa) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (hmac_auth, assinatura_b64, method, hmac_hash, sig_hash, utilizador_id, mensagem_id, public_key)
        )
    #guardar tambem o tipo de chave e qual o algoritmo simetrico
    elif method == 'random-key':
        cursor.execute(
            "INSERT INTO cofre (codigoDeAutenticacao, assinaturaDigital, tipoDeCifra, hmacHash, sigHash, utilizador_id, mensagem_id, keySource, typeSim, salt, iv) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (hmac_auth, assinatura_b64, method, hmac_hash, sig_hash, utilizador_id, mensagem_id, key_source, type_sim, salt, iv)
        )
    else:
        cursor.execute(
            "INSERT INTO cofre (codigoDeAutenticacao, assinaturaDigital, tipoDeCifra, hmacHash, sigHash,utilizador_id, mensagem_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (hmac_auth, assinatura_b64, method, hmac_hash, sig_hash, utilizador_id, mensagem_id)
        )

    cofre_id = cursor.lastrowid
    
    db.commit()

    return jsonify({
        "success": True,
        "message": "Message saved successfully!",
        "mensagem_id": mensagem_id,
        "private_key": private_key_data,
        "private_key_message": private_key_message,
        "vault_id": cofre_id
    }), 201

@app.route("/message/decrypt", methods=["POST"])
@login_required
def decrypt_message_route():
    #ir buscar a informação inicial
    cofre_id = request.form.get('vault_id')
    secret = request.form.get('secret')

    #verificar se a info existe
    if not cofre_id or not secret:
        return render_template('open_vault.html', error="Vault id and secret key are required!")

    #verificar se o utilizador está logged in e se é válido
    #se não redirecionar para o login
    token = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")
    try:
        if not token or not SECRET_KEY:
            raise Exception("Session expired")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return redirect(url_for('login'))
    
    email = decoded.get("email")

    #inicializar base de dados
    db = get_db()
    cursor = db.cursor()

    #verificar utilizador na base de dados
    user = cursor.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
    if not user:
        return render_template('open_vault.html', error="Invalid user.")

    user_id = user[0]
    
    #ir buscar todos os dados necessários para a desencriptar
    resultado = cursor.execute("""
        SELECT c.tipoDeCifra, c.mensagem_id, c.codigoDeAutenticacao, c.assinaturaDigital, 
            c.hmacHash, c.sigHash, c.pkRsa, c.keySource, c.typeSim, c.salt, c.iv
        FROM cofre c
        WHERE c.id = ?
    """, (cofre_id,)).fetchone()

    if not resultado:
        return render_template('open_vault.html', error="Vault not found!")
    
    mensagem = None

    if resultado:
        #this pk_rsa is only for EDIT PURPOSES
        method, mensagem_id, hmacAuth, signDig, hmacHash, sigHash, pk_rsa, key_source, type_sim , salt, iv = resultado

        row_mensagem = cursor.execute("""
            SELECT m.conteudoCifrado, m.titulo
            FROM mensagem m
            WHERE m.id = ?
        """, (mensagem_id,)).fetchone()

    if row_mensagem:
        conteudo_cifrado = row_mensagem[0]
        titulo = row_mensagem[1]
    else:
        return render_template('open_vault.html', error="Message not found!")


    #verificar o hmac do criptograma, de forma a saber se o mesmo sofreu altereações
    #recalculamos o hmac a partir do criptograma
    hmacNow = HMAC_authentication(hmacHash, conteudo_cifrado)
    hmacVer = False

    #comparamos com o hmac guardado
    if hmacNow == hmacAuth:
        hmacVer = True

    try:
        if method == "rsa":
            mensagem = decrypt_message_rsa(conteudo_cifrado, secret)
        elif method == "random-key":
            if key_source == 'passChosen':
                #pegar na palavra-passe que o user inseriu
                salt = base64.b64decode(salt)
                _, secretKey = deriveKey(secret, salt)
            else:
                #gerar pass random
                try:
                    secretKey = base64.b64decode(secret)
                except Exception:
                    return render_template('open_vault.html', error="The secret key is not valid")

            #verificar qual o algoritmo simetrico
            if type_sim == 'AES-256-CBC':
                mensagem = decrypt_AES_CBC(conteudo_cifrado, secretKey, iv)
            elif type_sim == 'AES-256-CTR':
                mensagem = decrypt_AES_CTR(conteudo_cifrado, secretKey, iv)
            elif type_sim == 'ChaCha20':
                mensagem = decrypt_chacha20(conteudo_cifrado, secretKey, iv)
            else:
                return jsonify({"success": False, "error": "Type of symmetric algorithm not supported"}), 501            
                
        if mensagem is None:
            return render_template('open_vault.html', error="Cipher method not supported.")

    except Exception as e:
        print(e)
        return render_template('open_vault.html', error="Decrypt fail. Verify the secret.")

    #verificar a assinatura digital do texto limpo
    sig_bytes = base64.b64decode(signDig)
    sigVer = verify_signature(sig_bytes, mensagem, sigHash)

    if method == "random-key" and key_source == "passChosen":
        _vault_secret_cache[(user_id, int(cofre_id))] = secret

    return render_template(
        'open_result.html',
        vault_id=cofre_id,
        hmac_ok=hmacVer,
        sig_ok=sigVer,
        title=titulo,
        message=mensagem   
    )

@app.route("/vault/<int:vault_id>/edit", methods=["GET", "POST"])
@login_required
def edit_vault(vault_id):
    db = get_db()
    cursor = db.cursor()

    vault = cursor.execute(
        """
        SELECT mensagem_id,
               utilizador_id,
               tipoDeCifra,
               keySource,
               typeSim,
               salt,
               iv,
               pkRsa,
               hmacHash,
               sigHash
        FROM cofre
        WHERE id = ?
        """,
        (vault_id,),
    ).fetchone()

    if not vault:
        return render_template(
            "open_result.html",
            vault_id=vault_id,
            hmac_ok=False,
            sig_ok=False,
            error="Vault not found!",
        ), 404

    mensagem_id, owner_id, method, key_source, type_sim, salt, iv, pk_rsa, hmac_hash, sig_hash = vault

    current = getattr(g, "current_user", None)
    if not current or "email" not in current:
        return redirect(url_for("login"))

    user = cursor.execute("SELECT id FROM user WHERE email = ?", (current.get("email"),)).fetchone()
    if not user or user[0] != owner_id:
        return render_template(
            "open_result.html",
            vault_id=vault_id,
            hmac_ok=False,
            sig_ok=False,
            error="Forbidden: only the creator can edit this vault",
        ), 403

    if request.method == "GET":
        title = request.args.get("title", "")
        message = request.args.get("message", "")

        if not title or not message:
            return render_template(
                "open_result.html",
                vault_id=vault_id,
                hmac_ok=False,
                sig_ok=False,
                error="Missing title or message to edit this vault.",
            ), 400

        return render_template(
            "edit_vault.html",
            vault_id=vault_id,
            title=title,
            message=message,
            method=method,
            needs_secret=(method == "random-key"),
            key_source=key_source,
            type_sim=type_sim,
        )

    title = request.form.get("title")
    message = request.form.get("message")
    secret = request.form.get("secret")

    if not title or not message:
        return render_template(
            "edit_vault.html",
            vault_id=vault_id,
            title=title or "",
            message=message or "",
            method=method,
            needs_secret=(method == "random-key"),
            key_source=key_source,
            type_sim=type_sim,
            error="Title and message are required.",
        ), 400

    if method == "rsa":
        if not pk_rsa:
                rsa_row = cursor.execute(
                    "SELECT pkRsa FROM rsaKey WHERE utilizador_id = ?",
                    (owner_id,),
                ).fetchone()

                if rsa_row:
                    pk_rsa = rsa_row[0]

        if not pk_rsa:
            return render_template(
                "edit_vault.html",
                vault_id=vault_id,
                title=title,
                message=message,
                method=method,
                needs_secret=False,
                key_source=key_source,
                type_sim=type_sim,
                error="Public key not found for this vault.",
            ), 500

        cryptogram = encrypt_message_rsa(message, pk_rsa)
        iv_value = None
        salt_value = None
    elif method == "random-key":
        if not secret and key_source == "passChosen":
            secret = _vault_secret_cache.get((owner_id, vault_id))

        if not secret:
            return render_template(
                "edit_vault.html",
                vault_id=vault_id,
                title=title,
                message=message,
                method=method,
                needs_secret=False,
                key_source=key_source,
                type_sim=type_sim,
                error="Open the vault first so the password-based key can be reused.",
            ), 400

        if key_source == "passChosen":
            if not salt:
                return render_template(
                    "edit_vault.html",
                    vault_id=vault_id,
                    title=title,
                    message=message,
                    method=method,
                    needs_secret=True,
                    key_source=key_source,
                    type_sim=type_sim,
                    error="Salt not found for this vault.",
                ), 500

            _, secretKey = deriveKey(secret, base64.b64decode(salt))
            salt_value = salt
        else:
            try:
                secretKey = base64.b64decode(secret)
            except Exception:
                return render_template(
                    "edit_vault.html",
                    vault_id=vault_id,
                    title=title,
                    message=message,
                    method=method,
                    needs_secret=True,
                    key_source=key_source,
                    type_sim=type_sim,
                    error="The secret key is not valid.",
                ), 400

            salt_value = salt

        if type_sim == "AES-256-CBC":
            cryptogram, iv_value = aes256_cbc_encrypt(message, secretKey, None)
        elif type_sim == "AES-256-CTR":
            cryptogram, iv_value = aes256_ctr_encrypt(message, secretKey, None)
        elif type_sim == "ChaCha20":
            cryptogram, iv_value = encrypt_chacha20(message, secretKey, None)
        else:
            return render_template(
                "edit_vault.html",
                vault_id=vault_id,
                title=title,
                message=message,
                method=method,
                needs_secret=True,
                key_source=key_source,
                type_sim=type_sim,
                error="Type of symmetric algorithm not supported.",
            ), 501
    else:
        return render_template(
            "edit_vault.html",
            vault_id=vault_id,
            title=title,
            message=message,
            method=method,
            needs_secret=False,
            key_source=key_source,
            type_sim=type_sim,
            error="Unsupported encryption method.",
        ), 400

    assinatura_b64 = base64.b64encode(sign_digitally(sig_hash, message)).decode("utf-8")
    hmac_auth = HMAC_authentication(hmac_hash, cryptogram.encode() if isinstance(cryptogram, str) else cryptogram)

    cursor.execute(
        "UPDATE mensagem SET titulo = ?, conteudoCifrado = ? WHERE id = ?",
        (title, cryptogram, mensagem_id),
    )

    if method == "rsa":
        cursor.execute(
            """
            UPDATE cofre
            SET codigoDeAutenticacao = ?,
                assinaturaDigital = ?,
                tipoDeCifra = ?,
                hmacHash = ?,
                sigHash = ?,
                pkRsa = ?
            WHERE id = ?
            """,
            (hmac_auth, assinatura_b64, method, hmac_hash, sig_hash, pk_rsa, vault_id),
        )
    else:
        cursor.execute(
            """
            UPDATE cofre
            SET codigoDeAutenticacao = ?,
                assinaturaDigital = ?,
                tipoDeCifra = ?,
                hmacHash = ?,
                sigHash = ?,
                keySource = ?,
                typeSim = ?,
                salt = ?,
                iv = ?
            WHERE id = ?
            """,
            (hmac_auth, assinatura_b64, method, hmac_hash, sig_hash, key_source, type_sim, salt_value, iv_value, vault_id),
        )

    db.commit()

    return render_template(
        "open_result.html",
        vault_id=vault_id,
        hmac_ok=True,
        sig_ok=True,
        title=title,
        message=message,
    )


@app.route("/vault/<int:vault_id>/delete")
@login_required
def delete_vault(vault_id):
    db = get_db()
    cursor = db.cursor()

    # obter cofre e verificar se existe
    row = cursor.execute(
        "SELECT mensagem_id, utilizador_id FROM cofre WHERE id = ?",
        (vault_id,),
    ).fetchone()

    if not row:
        return render_template(
            "open_result.html",
            vault_id=vault_id,
            hmac_ok=False,
            sig_ok=False,
            error="Vault not found!",
        )

    mensagem_id, owner_id = row

    # obter utilizador atual do token definido pelo decorador
    current = getattr(g, 'current_user', None)
    if not current or 'email' not in current:
        return redirect(url_for('login'))

    email = current.get('email')
    user = cursor.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
    if not user:
        return render_template(
            "open_result.html",
            vault_id=vault_id,
            hmac_ok=False,
            sig_ok=False,
            error="User not found",
        )

    user_id = user[0]
    if owner_id != user_id:
        return render_template(
            "open_result.html",
            vault_id=vault_id,
            hmac_ok=False,
            sig_ok=False,
            error="Forbidden: only the creator can delete this vault",
        ), 403

    cursor.execute("DELETE FROM cofre WHERE id = ?", (vault_id,))
    cursor.execute("DELETE FROM mensagem WHERE id = ?", (mensagem_id,))
    db.commit()

    return redirect(url_for("index"))



@app.route("/vault/request-delete", methods=["POST"])
def request_delete_vault():

    data = request.get_json()

    vault_id = data.get("vault_id")

    if not vault_id:
        return jsonify({"success": False, "error": "Missing data"}), 400

    db = get_db()
    cursor = db.cursor()

    token_cookie = request.cookies.get("token")
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not token_cookie or not SECRET_KEY:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    try:
        decoded = jwt.decode(token_cookie, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "Invalid token"}), 401

    email = decoded.get("email")

    user = cursor.execute(
        """
        SELECT id, username, email
        FROM user
        WHERE email = ?
        """,
        (email,),
    ).fetchone()

    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    user_id = user[0]

    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    vault = cursor.execute(
        """
        SELECT id
        FROM cofre
        WHERE id = ?
        AND utilizador_id = ?
        """,
        (vault_id, user_id),
    ).fetchone()

    if not vault:
        return jsonify({"success": False, "error": "Vault not found"}), 404

    token, expiration = gerar_delete_token()

    cursor.execute(
        """
        UPDATE cofre
        SET delete_token = ?,
            delete_token_expira = ?
        WHERE id = ?
        """,
        (token, expiration.isoformat(), vault_id),
    )

    db.commit()

    class TempUser:
        pass

    temp_user = TempUser()
    temp_user.username = user[1]
    temp_user.email = user[2]

    enviar_email_apagar_cofre(temp_user, vault_id, token)

    return jsonify({"success": True, "message": "Confirmation email sent"})


@app.route("/delete-vault-confirm")
def delete_vault_confirm_page():

    token = request.args.get("token")
    vault_id = request.args.get("vault_id")

    if not token or not vault_id:
        return "Invalid link", 400

    db = get_db()
    cursor = db.cursor()

    vault = cursor.execute(
        """
        SELECT delete_token,
                delete_token_expira,
                utilizador_id
        FROM cofre
        WHERE id = ?
        """,
        (vault_id,),
    ).fetchone()

    if not vault:
        return "Vault not found", 404

    saved_token, expiration, owner_id = vault

    saved_token = str(saved_token).strip()
    token = str(token).strip()

    print("TOKEN URL:", token)
    print("TOKEN BD:", saved_token)

    if saved_token != token:
        return "Invalid token", 400

    if not expiration:
        return "Invalid token", 400

    try:
        expiration_date = datetime.datetime.fromisoformat(expiration)
    except:
        return "Invalid token", 400

    if datetime.datetime.now() > expiration_date:
        return "Token expired", 400

    # exigir que o utilizador autenticado seja o criador do cofre
    token_cookie = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not token_cookie or not SECRET_KEY:
        return redirect(url_for('login'))

    try:
        decoded = jwt.decode(token_cookie, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return redirect(url_for('login'))

    email = decoded.get("email")
    user = cursor.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
    if not user:
        return redirect(url_for('login'))

    user_id = user[0]
    if owner_id != user_id:
        return "Forbidden: only the creator can delete this vault", 403

    print("TOKEN URL:", token)
    print("TOKEN BD:", saved_token)

    return render_template("delete_confirm.html")


@app.route("/vault/delete-confirm", methods=["POST"])
def confirm_delete_vault():

    data = request.get_json()

    token = data.get("token")
    vault_id = data.get("vault_id")

    if not token or not vault_id:
        return jsonify({"success": False, "error": "Missing token or vault id"}), 400

    db = get_db()
    cursor = db.cursor()

    # procurar cofre
    vault = cursor.execute(
        """
        SELECT id,
                delete_token,
                delete_token_expira,
                utilizador_id
        FROM cofre
        WHERE id = ?
        """,
        (vault_id,),
    ).fetchone()

    if not vault:
        return jsonify({"success": False, "error": "Vault not found"}), 404

    vault_id_db, saved_token, expiration, owner_id = vault

    # exigir que o utilizador autenticado seja o criador do cofre
    token_cookie = request.cookies.get('token')
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not token_cookie or not SECRET_KEY:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    try:
        decoded = jwt.decode(token_cookie, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "Invalid token"}), 401

    email = decoded.get("email")
    user = cursor.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    user_id = user[0]
    if owner_id != user_id:
        return jsonify({"success": False, "error": "Forbidden: only the creator can delete this vault"}), 403

    # validar token
    if saved_token != token:
        return jsonify({"success": False, "error": "Invalid token"}), 400

    if not expiration:
        return jsonify({"success": False, "error": "Invalid token"}), 400

    # validar data
    try:
        expiration_date = datetime.datetime.fromisoformat(expiration)
    except:
        return jsonify({"success": False, "error": "Invalid token"}), 400

    # verificar expiração
    if datetime.datetime.now() > expiration_date:
        return jsonify({"success": False, "error": "Token expired"}), 400

    # apagar cofre
    cursor.execute(
        """
        DELETE FROM cofre
        WHERE id = ? AND delete_token = ?
        """,
        (vault_id, token),
    )

    db.commit()

    return jsonify({"success": True, "message": "Vault deleted successfully"})





