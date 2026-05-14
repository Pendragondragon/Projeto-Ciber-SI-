import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user ( 
        id INTEGER PRIMARY KEY, 
        username TEXT, 
        email TEXT, 
        password TEXT,
        reset_token TEXT,
        reset_token_expira TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensagem (
        id INTEGER PRIMARY KEY, 
        titulo TEXT,
        conteudoCifrado TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS cofre (
        id INTEGER PRIMARY KEY,
        codigoDeAutenticacao TEXT,
        assinaturaDigital TEXT,
        tipoDeCifra TEXT,
        hmacHash TEXT,
        sigHash TEXT,
        utilizador_id INTEGER,
        mensagem_id INTEGER,
        FOREIGN KEY (utilizador_id) REFERENCES user(id),
        FOREIGN KEY (mensagem_id) REFERENCES mensagem(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS rsaKey (
        id INTEGER PRIMARY KEY,
        utilizador_id INTEGER,
        pkRsa TEXT,
        FOREIGN KEY (utilizador_id) REFERENCES user(id)
    )
""")

connection.commit()
connection.close()