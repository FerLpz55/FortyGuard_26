from pathlib import Path

import langchain_community
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "documents" / "Propuesta_OmniTherm_AI_v2.pdf"
CHROMA_PATH = BASE_DIR / "chroma_db"


print("📄 Cargando PDF...")

# 1. Leer el PDF
loader = langchain_community.document_loaders.PyPDFLoader(str(PDF_PATH))
documents = loader.load()

print(f"✅ Páginas cargadas: {len(documents)}")


# 2. Dividir el texto en fragmentos
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print(f"✂️ Fragmentos creados: {len(chunks)}")


# 3. Crear embeddings
print("🧠 Creando embeddings...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# 4. Guardar los embeddings en ChromaDB
print("🗄️ Guardando en ChromaDB...")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(CHROMA_PATH)
)

print("✅ RAG preparado correctamente.")
print(f"📁 Base vectorial: {CHROMA_PATH}")