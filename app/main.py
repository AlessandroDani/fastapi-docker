from fastapi import FastAPI, Request
import json
import os
import psycopg2
from dotenv import load_dotenv
from pydantic import BaseModel

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

class Nota(BaseModel):
    titulo: str
    contenido: str

@app.get("/")
async def root():
    return {
        "message": "Welcome to the FastAPI application! "
        "You can use this API to manage your notes."
    }

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

## The table had been created previously with the following command: 
# docker compose exec db psql -U usuario -d notasdb -c 
# "CREATE TABLE IF NOT EXISTS notas (id SERIAL PRIMARY KEY, contenido TEXT);"

@app.post("/notes")
async def create_note(nota: Nota):
    try:
        with open(DATA_FILE, "a") as f:
            f.write(f"{nota.titulo}: {nota.contenido}\n")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notas (titulo, contenido) VALUES (%s, %s)", (nota.titulo, nota.contenido))
        conn.commit()
    except Exception as e:
        return {"error": f"Error al guardar en la base de datos: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

    return {"mensaje": "Nota guardada correctamente"}

@app.get("/notes")
@app.get("/notes")
async def get_notes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, contenido FROM notas")
        rows = cursor.fetchall()

        notas = []
        for row in rows:
            if len(row) == 3:
                nota = {
                    "id": row[0],
                    "titulo": row[1],
                    "contenido": row[2]
                }
                notas.append(nota)

        return {"notas": notas}
    except Exception as e:
        return {"error": f"Error al consultar la base de datos: {str(e)}"}
    finally:
        cursor.close()
        conn.close()