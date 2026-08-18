import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI


# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"

# Cargar API Key
load_dotenv(BASE_DIR / ".env")


# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Conectarnos a ChromaDB
vectorstore = Chroma(
    persist_directory=str(CHROMA_PATH),
    embedding_function=embeddings
)


# Modelo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)


# Pregunta
pregunta = input("\n🤖 Pregunta sobre OmniTherm: ")


# Buscar información relevante
documentos = vectorstore.similarity_search(
    pregunta,
    k=4
)


# Crear contexto
contexto = "\n\n".join(
    documento.page_content
    for documento in documentos
)


# Crear prompt
prompt = f"""
Eres el asistente de IA de OmniTherm.

Responde la pregunta utilizando únicamente la información
proporcionada en el contexto.

Si la información no aparece en el contexto, responde:
"No encontré esa información en los documentos de OmniTherm."

Contexto:
{contexto}

Pregunta:
{pregunta}
"""


# Generar respuesta
respuesta = llm.invoke(prompt)

print("\n🤖 Respuesta:")

if isinstance(respuesta.content, list):
    for bloque in respuesta.content:
        if bloque.get("type") == "text":
            print(bloque.get("text", ""))
else:
    print(respuesta.content)