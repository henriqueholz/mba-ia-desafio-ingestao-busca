import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
    if not question:
        return "Por favor, forneça uma pergunta."

    # Vetorizar a pergunta (feito automaticamente pelo similarity_search)
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
    )

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME", "documents"),
        connection=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/rag"),
        use_jsonb=True,
    )

    # Buscar os 10 resultados mais relevantes (k=10) no banco vetorial
    results = store.similarity_search_with_score(question, k=10)

    # Montar o prompt com o contexto encontrado
    contexto = "\n\n".join([doc.page_content for doc, score in results])
    
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    formatted_prompt = prompt.format(contexto=contexto, pergunta=question)

    # Chamar a LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0
    )
    response = llm.invoke(formatted_prompt)

    # Retornar a resposta ao usuário
    return response.content

if __name__ == "__main__":
    search_prompt()