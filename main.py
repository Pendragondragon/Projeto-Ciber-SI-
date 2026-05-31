from flask import Flask, g
from flask_mail import Mail
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

app = Flask(__name__, template_folder='./resources/templates', static_folder='./resources/static')

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

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

from app.routes import *

if __name__ == "__main__":
    # app.run()
    # Use adhoc SSL for development and a non-privileged port
    app.run(host="127.0.0.1", port=5000, ssl_context='adhoc')


