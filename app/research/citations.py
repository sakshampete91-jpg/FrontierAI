from app.research.sources import (
    ResearchCitation,
    ResearchSource,
)


class CitationBuilder:
    """Creates citations from research sources."""

    def build(
        self,
        sources: list[ResearchSource],
    ) -> list[ResearchCitation]:
        citations: list[ResearchCitation] = []

        for index, source in enumerate(
            sources,
            start=1,
        ):
            citations.append(
                ResearchCitation(
                    citation_id=f"source-{index}",
                    source_id=source.source_id,
                    title=source.title,
                    url=source.url,
                )
            )

        return citations

    def format_markdown(
        self,
        citations: list[ResearchCitation],
    ) -> str:
        if not citations:
            return ""

        lines = [
            "Sources:"
        ]

        for citation in citations:
            lines.append(
                f"[{citation.citation_id}] "
                f"{citation.title} — {citation.url}"
            )

        return "\n".join(lines)