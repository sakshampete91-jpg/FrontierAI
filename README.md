\# FrontierAI



FrontierAI is a modular local AI assistant platform built around an

orchestration-first architecture.



\## Architecture



User

↓

AI Interface

↓

Context Manager

↓

Master Orchestrator

↓

Intent Understanding

↓

Task Planner

↓

Model Router

↓

Specialist Selection

↓

Tool Selection

↓

Knowledge Retrieval

↓

Memory Retrieval

↓

Execution

↓

Verification

↓

Response Generation

↓

Memory Update

↓

User



\## Core Features



\- Local AI inference with Ollama

\- Model Gateway and provider abstraction

\- Intent classification

\- Intelligent model routing

\- Task planning

\- Specialist handling

\- Tool registry

\- Safe calculator tool

\- Tool execution and verification

\- Persistent SQLite conversation memory

\- Memory retrieval

\- Knowledge/RAG pipeline

\- Document ingestion

\- Embedding-based retrieval

\- Web research pipeline

\- Source and citation handling

\- Prompt-injection protection

\- Global error handling

\- Request tracing

\- Structured observability

\- FastAPI backend

\- Browser-based frontend

\- Conversation history

\- One-click startup



\## Technology



\- Python

\- FastAPI

\- Pydantic

\- SQLite

\- Ollama

\- Qwen3 8B

\- Nomic Embed Text

\- HTML

\- CSS

\- JavaScript



\## Local Models



\### Chat Model



qwen3:8b



\### Embedding Model



nomic-embed-text



\## Requirements



\- Windows

\- Python 3.14+

\- Ollama

\- Installed local Ollama models

\- Virtual environment in `.venv`



\## Starting FrontierAI



Run:



&#x20;   start\_frontierai.bat



The launcher starts:



\- Ollama

\- FrontierAI API

\- Frontend



Frontend:



&#x20;   http://127.0.0.1:8000/



API documentation:



&#x20;   http://127.0.0.1:8000/docs



Health check:



&#x20;   http://127.0.0.1:8000/health



\## API



\### Chat



POST:



&#x20;   /chat



Example request:



&#x20;   {

&#x20;       "message": "Hello FrontierAI",

&#x20;       "conversation\_id": "demo"

&#x20;   }



\## Project Structure



&#x20;   backend/

&#x20;   │

&#x20;   ├── app/

&#x20;   │   ├── api/

&#x20;   │   ├── core/

&#x20;   │   ├── execution/

&#x20;   │   ├── intent/

&#x20;   │   ├── knowledge/

&#x20;   │   ├── memory/

&#x20;   │   ├── models/

&#x20;   │   ├── observability/

&#x20;   │   ├── orchestrator/

&#x20;   │   ├── planner/

&#x20;   │   ├── research/

&#x20;   │   ├── security/

&#x20;   │   ├── specialists/

&#x20;   │   ├── tools/

&#x20;   │   └── verification/

&#x20;   │

&#x20;   ├── data/

&#x20;   │   └── frontier\_memory.db

&#x20;   │

&#x20;   ├── .env

&#x20;   ├── start\_frontierai.bat

&#x20;   └── README.md



\## Safety



FrontierAI treats external research content as untrusted data.



External content must not be allowed to override:



\- System instructions

\- Developer instructions

\- User instructions

\- Tool permissions

\- Security policies



Tool execution is routed through registered tools and can enforce

permission requirements.



\## Verification



Important execution results can be independently verified before

being returned.



For example:



&#x20;   calculate 25\*4



The calculator executes the expression and the verification layer

checks the result independently.



\## Memory



FrontierAI stores conversation memory in SQLite.



Memory is separated using conversation IDs so different conversations

do not unintentionally share their context.



\## Observability



Requests produce structured trace events including:



\- memory\_loaded

\- memory\_retrieved

\- knowledge\_retrieved

\- intent\_classified

\- task\_routed

\- plan\_created

\- tool\_selected

\- specialist\_handled

\- request\_completed

\- request\_failed



\## Development Status



Core orchestration pipeline: COMPLETE



Local model integration: COMPLETE



Persistent memory: COMPLETE



Tool execution: COMPLETE



Verification: COMPLETE



RAG foundation: COMPLETE



Research foundation: COMPLETE



Security foundation: COMPLETE



Observability: COMPLETE



FastAPI API: COMPLETE



Frontend: COMPLETE



Startup automation: COMPLETE

