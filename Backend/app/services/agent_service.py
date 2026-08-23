import uuid
import os
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from app.agents.core import runner
from app.schemas.agent import AgentChatRequest, AgentChatResponse

logger = structlog.get_logger(__name__)

class KnowledgeBaseManager:
    """Manages the semantic search vectorstore for the FortyGuard RAG pipeline."""
    
    def __init__(self) -> None:
        # Inicializa una base de datos vectorial local en la carpeta 'data/chroma'
        persist_path = os.path.join(os.getcwd(), "data", "chroma")
        os.makedirs(persist_path, exist_ok=True)
        
        self.chroma_client = PersistentClient(path=persist_path)
        self.collection = self.chroma_client.get_or_create_collection("fortyguard_knowledge")
        
        logger.info("loading_embedding_model_start", model="all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("loading_embedding_model_success")
    
        self._seed_knowledge_base()

    def _seed_knowledge_base(self) -> None:
        """Seeds the vector store with initial FortyGuard cooling and mitigation insights."""
        # Verificamos si ya contiene documentos para no duplicar
        if self.collection.count() > 0:
            return
            
        seed_docs = [
            "FortyGuard solutions specialize in urban heat island mitigation using cool pavement coatings and thermodynamic surface optimization.",
            "Overcooling in HVAC systems usually occurs when setpoints drop below 21°C unnecessarily, spiking facility energy consumption by 15%.",
            "To reduce urban heat retention, high-albedo materials reflect solar radiation, keeping surface temperatures up to 10°C cooler.",
            "The optimum setpoint range for administrative buildings and commercial sites under FortyGuard optimization guidelines is 22.5°C to 24°C."
        ]
        
        embeddings = self.embedding_model.encode(seed_docs).tolist()
        ids = [f"seed_{i}" for i in range(len(seed_docs))]
        metadatas = [{"source": "fortyguard_guide"} for _ in seed_docs]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=seed_docs,
            metadatas=metadatas
        )
        logger.info("knowledge_base_seeded", count=self.collection.count())

    def query_context(self, query: str, n_results: int = 2) -> str:
        """Retrieves relevant text blocks based on semantic similarity."""
        query_embedding = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        if results and results.get("documents") and results["documents"][0]:
            return "\n".join(results["documents"][0])
        return ""

kb_manager = KnowledgeBaseManager()


class AgentService:
    """Orchestrates RAG pipelines and cognitive multi-agent processing."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        
    async def process_chat(self, payload: AgentChatRequest) -> AgentChatResponse:
        """Processes user message through a RAG pipeline and triggers agent reasoning."""
        logger.info("agent_chat_processing_start", message=payload.message, session_id=payload.session_id)
        
        # 1. Recuperar contexto relevante desde nuestra base de conocimientos vectorial (RAG)
        context = kb_manager.query_context(payload.message)
        
        # 2. Enriquecer el prompt del usuario con la información técnica recuperada
        enriched_prompt = payload.message
        if context:
            logger.info("rag_context_retrieved", length=len(context))
            enriched_prompt = (
                f"Use the following technical reference context to accurately answer the prompt if applicable:\n"
                f"### CONTEXT:\n{context}\n\n"
                f"### USER PROMPT:\n{payload.message}"
            )

        session_id = payload.session_id or f"session_{uuid.uuid4().hex[:8]}"

        agent_raw_response = runner.run(enriched_prompt)
        
        # 4. Construir y estructurar la respuesta acoplada al contrato de Pydantic v2
        response_dto = AgentChatResponse(
            response=str(agent_raw_response),
            actions_taken=[{"tool": "semantic_rag_search", "status": "success"}],
            session_id=session_id
        )
        
        logger.info("agent_chat_processing_success", session_id=session_id)
        return response_dto

    async def process_heat_alert(self, site_id: uuid.UUID, reading: Any) -> None:
        """Automated callback for heat alerts triggered by sensor telemetry."""
        logger.info("process_heat_alert_triggered", site_id=str(site_id), temp=reading.temperature_c)
        
        pass