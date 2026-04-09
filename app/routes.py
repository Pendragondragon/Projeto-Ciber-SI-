from main import app, get_db
from flask import render_template, request, jsonify

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("inicio.html")

@app.route("/register", methods=["POST"])
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

    cursor.execute("""
        INSERT INTO user (username, email, password)
        VALUES (?, ?, ?)
    """, (username, email, password))
    db.commit()

    return jsonify({"success": True, "message": "Utilizador registado com sucesso!"}), 201