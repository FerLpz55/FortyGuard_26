from app.rag.knowledge_base import KnowledgeBaseTool

knowledge_tool = KnowledgeBaseTool()

async def query_knowledge_base(question: str) -> dict:
    """Consulta procedimientos, normativas y best practices del RAG corporativo."""
    result = await knowledge_tool.query(question)
    return {
        "question": question, 
        "answer": result.get("answer"), 
        "source": "omnitherm_rag"
    }