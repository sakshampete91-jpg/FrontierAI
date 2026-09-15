from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ResearchSource:
    """A source used during a FrontierAI research task."""

    source_id: str
    title: str
    url: str
    snippet: str = ""
    extracted_text: str = ""
    source_type: str = "web"
    accessed_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ResearchCitation:
    """A citation pointing to a research source."""

    citation_id: str
    source_id: str
    title: str
    url: str