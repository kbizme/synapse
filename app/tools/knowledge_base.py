from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool
import os


class KnowledgeBaseInput(BaseModel):
    query: str = Field(description="The search query to look up in the uploaded documents.")

    class Config:
        extra = 'allow'

EMBEDDINGS = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')


@tool('query_knowledge_base', args_schema=KnowledgeBaseInput)
def query_knowledge_base(query: str, chat_id: str):
    """
    Search through the user's uploaded documents (PDFs, text files) to find answers 
    to questions based on specific local knowledge. Use this tool whenever the user 
    asks about content they have uploaded.
    """
    persist_dir = './chroma_db'
    collection_name = f'chat_{chat_id}'
    
    if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
        return "No knowledge base found"
    
    vectod_db = Chroma(persist_directory=persist_dir, 
                embedding_function=EMBEDDINGS, 
                collection_name=collection_name)
    
    docs = vectod_db.similarity_search(query, k=3)
    if not docs:
        return " No relevant information found"
    
    context = "\n---\n".join([doc.page_content for doc in docs])
    return f"Information found in uploaded documents:\n\n{context}"

    