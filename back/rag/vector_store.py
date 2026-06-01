"""
pgvector-based vector store.
Run this SQL once to enable the extension and create the table:
 
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL,
        source VARCHAR(255),
        embedding vector(1536)
    );
    CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);
"""

from typing import List
from back.core.database import AsyncSessionLocal
from back.rag.retrieval import embed_text
from sqlalchemy import text

async def similarity_search(query:str, top_k:int=5) -> List[dict]:
    query_embedding = await embed_text(query)
    vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT text, source
                FROM knowledge_chunks
                ORDER BY embedding <-> :vec
                LIMIT :top_k
            """),
            {"vec": vec_str, "top_k": top_k}
        )
        rows = result.fetchall()
        return [
            {"id": r.id, "text": r.text, "source": r.source, "score": float(r.score)}
            for r in rows
        ]
    
async def upsert_chunk(text:str, source:str) -> None:
    embedding = await embed_text(text)
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"

    async with AsyncSessionLocal() as db:
        await db.execute(
            text("""
                INSERT INTO knowledge_chunks (text, source, embedding)
                VALUES (:text, :source, :embedding)
            """),
            {"text": text, "source": source, "embedding": vec_str}
        )
        await db.commit()

    

