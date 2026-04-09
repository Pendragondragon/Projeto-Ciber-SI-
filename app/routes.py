from main import app, get_db
from flask import render_template, request, jsonify
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route("/auth/login")
def login():
    return render_template("login.html")

@app.route("/auth/register", methods=["GET"])
def register_page():
    return render_template("inicio.html")

@app.route("/auth/register", methods=["POST"])
def register():
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