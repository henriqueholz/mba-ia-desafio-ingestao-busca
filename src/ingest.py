import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

def ingest_pdf():
    """
    Função principal para ingestão do PDF:
    1. Carrega o PDF
    2. Divide em chunks de 1000 caracteres com overlap de 150
    3. Converte cada chunk em embedding
    4. Armazena os vetores no PostgreSQL com pgVector
    """
    for k in ("DATABASE_URL","OPENAI_API_KEY"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

    PDF_PATH = "./document.pdf"

    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    # O PDF deve ser dividido em chunks de 1000 caracteres com overlap de 150.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150, 
        add_start_index=False
    )
    splits = text_splitter.split_documents(docs)
    
    if not splits:
        raise SystemExit(0)
    
    # Cada chunk deve ser convertido em embedding.
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Os vetores devem ser armazenados no banco de dados PostgreSQL com pgVector.
    connection_string = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/rag")
    
    store = PGVector(
        embeddings=embeddings,
        collection_name="documents",
        connection=connection_string,
        use_jsonb=True,
    )

    # Adicionar os documentos ao vector store (isso converte em embeddings e armazena)
    store.add_documents(splits)
    print(f"{len(splits)} chunks foram processados e armazenados no banco de dados")
    
    return store


if __name__ == "__main__":
    ingest_pdf()