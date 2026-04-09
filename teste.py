import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("""
    INSERT INTO user (username, email, password)
    VALUES (?, ?, ?)
""", ("Amilcar", "amilcar@email.com", "caramil"))

connection.commit()
connection.close()

print("User inserido com sucesso!")
