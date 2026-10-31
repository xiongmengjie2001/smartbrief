"""RAG 知识库封装。

采用经典分层结构（loaders / chunkers / embeddings / vectorstores），两处设计约束：
1. 配置读取：统一从 `backend/.env`（EMBEDDING_* 前缀）读取；2. 数据目录：模板/术语/持久化目录收敛到 `backend/data/` 下。
"""
from rag.embeddings import Embeddings, SiliconFlowEmbeddings, create_embeddings
from rag.loaders import Document, DocumentLoader, load_document
from rag.chunkers import BaseChunker, RecursiveChunker
from rag.vectorstores import ChromaVectorStore

__all__ = [
    "Embeddings",
    "SiliconFlowEmbeddings",
    "create_embeddings",
    "Document",
    "DocumentLoader",
    "load_document",
    "BaseChunker",
    "RecursiveChunker",
    "ChromaVectorStore",
]
