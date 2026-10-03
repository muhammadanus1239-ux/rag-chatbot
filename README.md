# RAG Chatbot

A multi-user Retrieval-Augmented Generation (RAG) chatbot built with FastAPI, PostgreSQL, pgvector, FastEmbed, and an OpenAI-compatible LLM API.

The application allows users to upload PDF/TXT documents, search their documents using vector similarity, and ask questions based on the retrieved document context.

## Features

- User registration and login
- JWT-based authentication
- PDF and TXT document upload
- Automatic text extraction
- Text chunking with overlap
- Vector embeddings using FastEmbed
- PostgreSQL with pgvector
- Cosine similarity search
- Retrieval-Augmented Generation (RAG)
- LLM-based question answering
- Source chunks returned with answers
- User-specific document isolation
- Chat history
- Automated tests with Pytest
- Docker and Docker Compose support
- FastAPI interactive Swagger documentation

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| FastAPI | Backend REST API |
| PostgreSQL | Database |
| pgvector | Vector storage and similarity search |
| SQLAlchemy | Database ORM |
| Alembic | Database migrations |
| FastEmbed | Text embeddings |
| OpenAI SDK | LLM API integration |
| Docker | Containerization |
| Pytest | Automated testing |

## RAG Architecture

The application follows this workflow:

```text
                DOCUMENT UPLOAD
                       |
                       v
              Extract Text (PDF/TXT)
                       |
                       v
                 Chunk Text
                       |
                       v
               Generate Embeddings
                       |
                       v
            PostgreSQL + pgvector
                       |
                       |
                       v
                  USER QUESTION
                       |
                       v
               Generate Embedding
                       |
                       v
             Vector Similarity Search
                       |
                       v
             Retrieve Relevant Chunks
                       |
                       v
                    LLM API
                       |
                       v
              Answer + Sources
```

## Document Processing

Uploaded documents are processed as follows:

1. The user uploads a PDF or TXT file.
2. The application extracts the document text.
3. The text is divided into chunks.
4. Each chunk is converted into an embedding vector.
5. The vectors are stored in PostgreSQL using pgvector.
6. The original chunk content is stored with its document information.

The current chunking configuration uses:

- Chunk size: 500 characters
- Overlap: 50 characters

## Embedding Model

The project uses:

```text
BAAI/bge-small-en-v1.5
```

The embedding dimension is:

```text
384
```

## Retrieval

When a user asks a question:

1. The question is converted into an embedding.
2. PostgreSQL/pgvector calculates cosine distance between the question vector and stored document vectors.
3. The most relevant chunks are retrieved.
4. Only documents belonging to the authenticated user are considered.
5. Retrieved chunks are passed to the LLM as context.

The default number of retrieved chunks is 3, with the API allowing up to 10.

## User Data Isolation

Each document belongs to a specific user.

During retrieval, the application filters documents using the authenticated user's ID.

This means a user cannot retrieve another user's private documents through the search or chat endpoints.

The project was manually tested with multiple users to verify this behavior.

## Authentication

The application uses JWT-based authentication.

Available authentication endpoints:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

After login, the returned access token is used to access protected endpoints.

## API Endpoints

### Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Documents

```text
POST /documents/upload
```

Supported document formats:

```text
.pdf
.txt
```

Maximum upload size:

```text
5 MB
```

### Search

```text
GET /search?q=<question>&top_k=<number>
```

The search endpoint returns the most relevant document chunks for the authenticated user.

### Chat

```text
POST /chat
```

The chat endpoint:

- retrieves relevant document chunks
- sends the context to the LLM
- generates an answer
- returns the answer with source information
- stores the conversation in chat history

### Chat History

```text
GET /chat/history
```

Returns the authenticated user's chat messages.

## Example RAG Request

A user uploads a document containing:

```text
User 2's secret project name is Project Phoenix.
```

The user can then ask:

```text
What is User 2's secret project?
```

The system retrieves the relevant document chunk and provides the answer using the retrieved context.

If the required information is not present in the retrieved context, the LLM is instructed not to invent an answer.

## Project Structure

```text
rag-chatbot/
│
├── alembic/
│   └── Database migration files
│
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── chat.py
│   │       ├── documents.py
│   │       └── search.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── chunk.py
│   │   ├── document.py
│   │   ├── message.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── document.py
│   │   ├── search.py
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── embeddings.py
│   │   ├── ingestion.py
│   │   ├── llm.py
│   │   └── retrieval.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_api.py
│   ├── test_chunking.py
│   └── test_security.py
│
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
├── requirements.txt
├── commands.txt
├── .dockerignore
└── .gitignore
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/muhammadanus1239-ux/rag-chatbot.git
cd rag-chatbot
```

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

The application reads environment variables from `.env`.

Required settings include:

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
LLM_API_KEY=your_llm_api_key
LLM_MODEL=your_llm_model
```

Do not commit the real `.env` file or API keys to GitHub.

### 5. Start PostgreSQL

The project includes PostgreSQL with pgvector through Docker Compose.

```powershell
docker compose up -d db
```

### 6. Run migrations

```powershell
alembic upgrade head
```

### 7. Start the API

```powershell
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Docker Setup

The project includes a complete Docker Compose setup with:

- PostgreSQL + pgvector database
- FastAPI application
- Persistent PostgreSQL storage
- Persistent uploaded files
- Persistent FastEmbed model cache
- Automatic Alembic migrations

Start the complete application:

```powershell
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Stop the containers:

```powershell
docker compose down
```

## Testing

Run the automated tests:

```powershell
pytest -q
```

Current test result:

```text
10 passed
```

The tests cover API functionality, text chunking, and security-related behavior.

## Security Considerations

The application includes:

- Password hashing
- JWT authentication
- Authenticated protected routes
- User-specific document filtering
- User-specific chat history
- `.env` excluded from Git
- Uploaded files excluded from Git

The retrieval query ensures that only documents belonging to the authenticated user are searched.

## Database

The application uses PostgreSQL with the pgvector extension.

Main database entities include:

```text
users
documents
chunks
messages
```

Document chunks contain their embedding vectors, allowing semantic similarity search.

## Development Commands

Run tests:

```powershell
pytest -q
```

Run the development server:

```powershell
uvicorn app.main:app --reload
```

Run migrations:

```powershell
alembic upgrade head
```

Start Docker:

```powershell
docker compose up --build
```

Stop Docker:

```powershell
docker compose down
```

## Project Status

The core RAG backend is implemented and tested.

Current automated test status:

```text
10 passed
```

The application supports document ingestion, vector retrieval, authenticated chat, source tracking, chat history, and user-level document isolation.

## Author

**Muhammad Anus**

GitHub:  
https://github.com/muhammadanus1239-ux