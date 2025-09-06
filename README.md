# Desafio MBA Engenharia de Software com IA - Full Cycle

Descreva abaixo como executar a sua solução.
Subir o banco de dados:

## Pré-requisitos

- Docker e Docker Compose
- Python
- Chave da API OpenAI

## Configuração do Ambiente

### 1. Instalar dependências Python

<pre>
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
</pre>

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto ou exporte as variáveis:

<pre>
# Banco de dados
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/rag

# Google AI (obrigatório)
GOOGLE_API_KEY=sua_chave_googleai_aqui

# Opcional - modelos específicos
GOOGLE_EMBEDDING_MODEL='models/embedding-001'
</pre>

## Execução

### 1. Subir o banco de dados PostgreSQL com pgVector

<pre>
docker compose up -d
</pre>

Aguarde alguns segundos para o banco inicializar completamente.

### 2. Executar ingestão do PDF

<pre>
# Ativar ambiente virtual
source venv/bin/activate

# Executar ingestão
python src/ingest.py
</pre>

Este comando irá:
- Carregar o arquivo `document.pdf`
- Dividir em chunks de 1000 caracteres
- Gerar embeddings usando OpenAI
- Armazenar no banco vetorial

### 3. Rodar o chat interativo

<pre>
# Ativar ambiente virtual (se não estiver ativo)
source venv/bin/activate

# Iniciar chat
python src/chat.py
</pre>

Digite suas perguntas sobre o documento. Use `sair`, `quit` ou `exit` para encerrar.

## Decisões Técnicas e Troubleshooting

### Por que Google AI em vez de OpenAI?

- **Custo**: Google AI oferece uma tier gratuita generosa
- **Performance**: `models/embedding-001` e `gemini-2.5-flash-lite` têm boa qualidade
- **Disponibilidade**: Menos restrições de quota para desenvolvimento

### Por que k=20 em vez de k=10?

Durante os testes, descobrimos que algumas consultas não retornavam resultados esperados com k=10. 

**Problema identificado:**
- Certas informações específicas (como "SuperTechIABrazil") tinham scores de similaridade mais baixos
- Com k=10, essas informações ficavam fora do top 10 resultados mais similares
- O sistema respondia "Não tenho informações necessárias" mesmo tendo os dados no PDF

**Solução:**
- Aumentamos para k=20 para capturar mais resultados, incluindo aqueles com similaridade moderada
- Isso melhorou significativamente a cobertura das respostas sem impactar a performance
