from fastapi import FastAPI, Request
import json
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
DATA_FILE = "/data/notas.txt"

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


@app.get("/")
async def root():
    return {
        "message": "Welcome to the FastAPI application! "
        "You can use this API to manage your notes."
    }

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.post("/notes")
async def create_note(request: Request):
    nota = await request.body()
    nota_texto = nota.decode()

    with open(DATA_FILE, "a") as f:
        f.write(nota_texto + "\\n")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notas (contenido) VALUES (%s)", (nota_texto,))
        conn.commit()
    except Exception as e:
        return {"error": f"Error al guardar en la base de datos: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

    return {"mensaje": "Nota guardada"}

@app.get("/notes")
async def get_notes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, contenido FROM notas")
        notas = [{"id": row[0], "contenido": row[1]} for row in cursor.fetchall()]
        return {"notas": notas}
    except Exception as e:
        return {"error": f"Error al consultar la base de datos: {str(e)}"}
    finally:
        cursor.close()
        conn.close()