from typing import Dict, Optional
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings


class KnowledgeBaseTool:
    """Tool de conocimiento para el agente ADK.

    refactoriza query.py a una clase
    reutilizable e importable, manteniendo el pipeline RAG original.
    """

    def __init__(
        self,
        chroma_path: Optional[str] = None,
        model_name: str = "gemini-3.6-flash",
        temperature: float = 0,
    ):
        current_settings = get_settings()
        configured_path = getattr(current_settings, "CHROMA_PATH", "../../chroma_db")
        
        self.chroma_path = Path(chroma_path or configured_path)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(
            persist_directory=str(self.chroma_path),
            embedding_function=self.embeddings,
        )
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

    async def query(
        self,
        question: str,
        k: int = 4,
        filter_metadata: Optional[Dict] = None,
    ) -> Dict:
        """Consulta la base de conocimiento y retorna respuesta contextualizada."""
        docs = self.vectorstore.similarity_search(
            question,
            k=k,
            filter=filter_metadata,
        )
        context = "\n\n".join(d.page_content for d in docs)

        prompt = self._build_prompt(question, context)
        response = await self.llm.ainvoke(prompt)

        return {
            "question": question,
            "answer": response.content,
            "sources": [
                {"content": d.page_content[:200], "metadata": d.metadata}
                for d in docs
            ],
        }

    def _build_prompt(self, question: str, context: str) -> str:
        """Prompt especializado OmniTherm (mejora sobre el original de Lilly)."""
        return (
            "Eres el asistente técnico de OmniTherm AI, specialized en:\n"
            "- Inteligencia térmica (FortyGuard Temperature API, LTMs)\n"
            "- Protección industrial (riesgo calor, seguridad laboral)\n"
            "- Eficiencia energética en edificios (HVAC, ASHRAE, ROI)\n\n"
            "Responde usando ÚNICAMENTE la información del contexto.\n"
            "Si la información NO está en el contexto, responde:\n"
            '"No encontré esa información en la base de conocimiento de OmniTherm."\n\n'
            "Cita la fuente cuando sea posible.\n\n"
            f"CONTEXTO:\n{context}\n\n"
            f"PREGUNTA: {question}\n\n"
            "RESPUESTA TÉCNICA Y ACCIONABLE:\n"
        )