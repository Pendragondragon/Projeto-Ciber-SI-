from main import app, get_db
from flask import render_template, request, jsonify
from flask_bcrypt import Bcrypt
from services.auth_service import gerar_token_recuperacao, validar_token
from services.email_service import enviar_email_recuperacao
import os
from dotenv import load_dotenv
import jwt
import datetime
from functools import wraps

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
