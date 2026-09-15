from app.context.manager import ContextManager
from app.core.config import settings
from app.execution.engine import ExecutionEngine

from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.embeddings import OllamaEmbeddingService
from app.knowledge.hybrid_retriever import (
    HybridKnowledgeRetriever,
)
from app.knowledge.ingestion import KnowledgeIngestionService
from app.knowledge.pdf_ingestion import (
    PDFKnowledgeIngestionService,
)
from app.knowledge.retriever import KnowledgeRetriever
from app.knowledge.semantic_retriever import (
    SemanticKnowledgeRetriever,
)
from app.knowledge.sqlite import SQLiteKnowledgeStore
from app.knowledge.vector_store import SQLiteVectorStore

from app.memory.retriever import MemoryRetriever
from app.memory.sqlite import SQLiteConversationStore

from app.models.gateway import ModelGateway
from app.models.ollama import OllamaProvider

from app.orchestrator.orchestrator import MasterOrchestrator

from app.research.citations import CitationBuilder
from app.research.fetcher import WebSourceFetcher
from app.research.free_provider import FreeSearchProvider
from app.research.pipeline import ResearchPipeline
from app.research.service import ResearchSearchService

from app.specialists.coding import CodingSpecialist
from app.specialists.general import GeneralSpecialist
from app.specialists.mathematics import MathematicsSpecialist
from app.specialists.registry import SpecialistRegistry
from app.specialists.research import ResearchSpecialist

from app.tools.calculator import calculate
from app.tools.registry import ToolDefinition, ToolRegistry
from app.tools.selection.selector import ToolSelector

from app.verification.engine import VerificationEngine


def create_orchestrator() -> MasterOrchestrator:
    """Create and configure FrontierAI's core dependencies."""

    gateway = ModelGateway()

    gateway.register_provider(
        "ollama",
        OllamaProvider(
            model=settings.ollama_model,
            host=settings.ollama_host,
        ),
        default=True,
    )

    tool_registry = ToolRegistry()

    tool_registry.register(
        ToolDefinition(
            name="calculator",
            description=(
                "Safely performs basic mathematical calculations."
            ),
            handler=calculate,
            input_schema={
                "expression": str,
            },
        )
    )

    execution_engine = ExecutionEngine(
        tool_registry
    )

    verification_engine = VerificationEngine()

    memory_store = SQLiteConversationStore(
        "data/frontier_memory.db"
    )

    memory_retriever = MemoryRetriever()

    knowledge_database = (
        "data/frontier_knowledge.db"
    )

    knowledge_document_store = (
        SQLiteKnowledgeStore(
            knowledge_database
        )
    )

    knowledge_chunk_store = (
        SQLiteKnowledgeChunkStore(
            knowledge_database
        )
    )

    vector_store = SQLiteVectorStore(
        knowledge_database
    )

    embedding_service = (
        OllamaEmbeddingService()
    )

    keyword_retriever = KnowledgeRetriever(
        knowledge_chunk_store
    )

    semantic_retriever = (
        SemanticKnowledgeRetriever(
            vector_store,
            embedding_service,
        )
    )

    hybrid_retriever = (
        HybridKnowledgeRetriever(
            keyword_retriever,
            semantic_retriever,
            keyword_weight=0.3,
            semantic_weight=0.7,
        )
    )

    knowledge_ingestion = (
        KnowledgeIngestionService(
            document_store=knowledge_document_store,
            chunk_store=knowledge_chunk_store,
            vector_store=vector_store,
            embedding_service=embedding_service,
        )
    )

    pdf_ingestion = (
        PDFKnowledgeIngestionService(
            document_store=knowledge_document_store,
            chunk_store=knowledge_chunk_store,
            vector_store=vector_store,
            embedding_service=embedding_service,
        )
    )

    _ = knowledge_ingestion
    _ = pdf_ingestion

    context_manager = ContextManager(
        max_memory_items=5,
        max_knowledge_items=5,
    )

    tool_selector = ToolSelector(
        tool_registry,
    )

    # ---------------------------------------------------------
    # FREE RESEARCH SEARCH
    # ---------------------------------------------------------
    web_search_provider = (
        FreeSearchProvider(
            timeout=15,
        )
    )

    research_search_service = (
        ResearchSearchService(
            web_search_provider
        )
    )

    web_source_fetcher = WebSourceFetcher(
        timeout=15,
        max_bytes=1_000_000,
    )

    citation_builder = CitationBuilder()

    research_pipeline = ResearchPipeline(
        search_service=research_search_service,
        fetcher=web_source_fetcher,
        citation_builder=citation_builder,
    )

    specialist_registry = SpecialistRegistry()

    specialist_registry.register(
        GeneralSpecialist(gateway)
    )

    specialist_registry.register(
        CodingSpecialist(gateway)
    )

    specialist_registry.register(
        ResearchSpecialist(
            gateway,
            research_pipeline,
        )
    )

    specialist_registry.register(
        MathematicsSpecialist(gateway)
    )

    return MasterOrchestrator(
        gateway,
        execution_engine=execution_engine,
        verification_engine=verification_engine,
        memory_store=memory_store,
        memory_retriever=memory_retriever,
        context_manager=context_manager,
        tool_registry=tool_registry,
        tool_selector=tool_selector,
        specialist_registry=specialist_registry,
        knowledge_retriever=hybrid_retriever,
        research_pipeline=research_pipeline,
    )