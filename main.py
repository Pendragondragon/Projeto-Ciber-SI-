from flask import Flask, g
import sqlite3

app = Flask(__name__, template_folder='./resources/templates', static_folder='./resources/static')

from app.routes import *

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run()