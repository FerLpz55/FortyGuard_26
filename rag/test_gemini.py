import os
from dotenv import load_dotenv

load_dotenv()

print("API KEY CARGADA:", bool(os.getenv("GOOGLE_API_KEY")))

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv("../.env")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)

respuesta = llm.invoke(
    "Explica qué es un sistema RAG en una sola frase."
)

print(respuesta.content)