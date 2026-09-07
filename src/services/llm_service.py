import os
import re
from google import genai
from sqlalchemy.orm import Session
from src.database import RecordModel as Record

# Inicializar cliente oficial con la API key del entorno
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_database(db: Session, question: str) -> tuple[str, list[int]]:
    if not question:
        return "Por favor, ingresa una pregunta válida.", []

    # Limpiar la pregunta y extraer la última palabra relevante omitiendo signos de puntuación
    clean_question = re.sub(r'[^\w\s]', '', question)
    words = clean_question.split()
    query_keyword = words[-1] if words else ""

    # 1. Recuperación focalizada segura
    records = []
    if query_keyword:
        records = db.query(Record).filter(
            (Record.full_name.ilike(f"%{query_keyword}%")) |
            (Record.company_name.ilike(f"%{query_keyword}%"))
        ).limit(5).all()

    # 2. Si no hay coincidencias con la última palabra, intentar traer los últimos registros generales como respaldo
    if not records:
        records = db.query(Record).order_by(Record.id.desc()).limit(5).all()

    if not records:
        return "No encontré información relevante en los registros para responder a tu pregunta.", []

    # 3. Construir contexto acotado y recolectar IDs
    context_chunks = []
    source_ids = []
    for r in records:
        source_ids.append(r.id)
        context_chunks.append(f"ID: {r.id} | Nombre: {r.full_name} | Empresa: {r.company_name} | Estado: {r.status}")

    context_str = "\n".join(context_chunks)

    prompt = f"""
    Responde a la pregunta del usuario basándote exclusivamente en el siguiente contexto. 
    Si la respuesta no está en el contexto, indica que no posees la información.

    Contexto:
    {context_str}

    Pregunta: {question}
    """

    try:
        # 4. Llamada al LLM con Gemini Flash
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text, source_ids
    except Exception as e:
        return f"Error al comunicarse con el servicio de IA: {str(e)}", []