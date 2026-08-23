from app.rag.knowledge_base import KnowledgeBaseTool

# Instancia global del tool reutilizable
knowledge_tool = KnowledgeBaseTool()


async def query_knowledge_base(question: str, k: int = 4) -> dict:
    """Consulta la base de conocimiento (RAG) para normativas y best practices."""
    return await knowledge_tool.query(question, k=k)