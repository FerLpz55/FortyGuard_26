
"""Agrega: múltiples fuentes, metadata por documento, soporte PDF y texto plano.
"""
from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DOCUMENTS_CONFIG: List[Dict] = [
    {
        "path": "../../documents/Propuesta_OmniTherm_AI_v2.pdf",
        "metadata": {"source": "propuesta", "category": "negocio", "type": "pdf"},
    },
    {
        "path": "../../documents/fortyguard_api_docs.txt",
        "metadata": {"source": "fortyguard", "category": "api", "type": "txt"},
    },
    {
        "path": "../../documents/osha_heat_safety.txt",
        "metadata": {"source": "osha", "category": "normativa", "type": "txt"},
    },
    {
        "path": "../../documents/ashrae_55_90.txt",
        "metadata": {"source": "ashrae", "category": "estandar", "type": "txt"},
    },
    {
        "path": "../../documents/epa_heat_island.txt",
        "metadata": {"source": "epa", "category": "guia", "type": "txt"},
    },
]


def load_document(path: str, metadata: Dict) -> List:
    """Carga documento según tipo de archivo."""
    if path.endswith(".pdf"):
        loader = PyPDFLoader(path)
    else:
        loader = TextLoader(path)

    docs = loader.load()
    for doc in docs:
        doc.metadata.update(metadata)
    return docs


def ingest_all(chroma_path: str) -> None:
    """Ingesta todos los documentos configurados a ChromaDB."""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    all_chunks = []
    for config in DOCUMENTS_CONFIG:
        path = config["path"]
        if not Path(path).exists():
            print(f"Saltando {path} (no existe)")
            continue

        docs = load_document(path, config["metadata"])
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)
        print(f"Cargado {path}: {len(chunks)} chunks")

    if not all_chunks:
        print("No se encontraron documentos nuevos para ingestar.")
        return

    Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=chroma_path,
    )
    print(f"Total chunks ingeridos con éxito: {len(all_chunks)}")


if __name__ == "__main__":

    ingest_all("../../chroma_db")