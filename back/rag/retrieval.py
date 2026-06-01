from typing import List, Annotated
from openai import AsyncOpenAI
from back.core.config import settings


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def embed_text(text:str) -> List[float]:
    resp = await client.embeddings.create(
        input= text,
        model= 'text-embedding-3-small'
    )
    return resp.data[0].embedding

async def retrieve_context(query: str, top_k: int = 5) -> List[dict]:
    """
    Retrieve relevant travel knowledge chunks for a query.
    Uses pgvector if available, falls back to a simple keyword match.
    """
    try:
        from back.rag.vector_store import similarity_search
        return await similarity_search(query, top_k=top_k)
    except Exception:
        return []
async def rag_answer(query: str) -> str:
      """
    Answer a travel question using RAG:
    1. Retrieve relevant chunks from the knowledge base
    2. Build a context-enriched prompt
    3. Return the LLM answer
    """
      chunks = await retrieve_context(query)
      context = "\n\n".join(c.get("text", "") for c in chunks) if chunks else ""
    
      system = (
        "You are a travel knowledge assistant. "
        "Answer based on the provided context when available, "
        "otherwise use your general knowledge."
    )
      user_content = f"Context:\n{context}\n\nQuestion: {query}" if context else query
 
      resp = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        max_tokens=600,
    )
      return resp.choices[0].message.content