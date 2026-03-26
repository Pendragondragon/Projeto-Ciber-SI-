from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
def home():
    return "ola"


@app.get("/login")
def login():
    return FileResponse(BASE_DIR / "templates" / "login.html")


@app.get("/style.css")
def style():
    return FileResponse(BASE_DIR / "static" / "css" / "input.css")