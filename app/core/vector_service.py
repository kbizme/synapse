from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os



class VectorService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = './chroma_db'
        self.base_upload_dir = './uploads'
        
    
    async def ingest_file(self, file_content: bytes, filename: str, chat_id: str) -> str:
        chat_sir = os.path.join(self.base_upload_dir, chat_id)
        
        # creating the chat directory
        if not os.path.exists(chat_sir):
            os.makedirs(chat_sir, exist_ok=True)
        
        # writing the file
        file_path = os.path.join(chat_sir, filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # transforming into documents object
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif filename.endswith('.txt'):
            loader = TextLoader(file_path)
        else:
            # TODO: need to handle this
            raise ValueError(f"Unsupported file type: {filename}")
        
        document = loader.load()
        
        # making chunk of the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(document)
        
        # vectorizing and saving into chromadb
        Chroma.from_documents(documents=chunks,
                              embedding=self.embeddings,
                              persist_directory=self.persist_directory,
                              collection_name=f'chat_{chat_id}')
        
        return file_path
        
        
        
        
