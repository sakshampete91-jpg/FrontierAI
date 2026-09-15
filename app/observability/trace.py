from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any


@dataclass
class TraceEvent:
    """A single event recorded during request processing."""

    name: str
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Trace containing the major steps of a FrontierAI request."""

    request_id: str
    events: list[TraceEvent] = field(default_factory=list)

    _started_at: float = field(
        default_factory=perf_counter,
        repr=False,
    )

    def add_event(
        self,
        name: str,
        **data: Any,
    ) -> None:
        self.events.append(
            TraceEvent(
                name=name,
                timestamp=datetime.now(
                    timezone.utc
                ),
                data=data,
            )
        )

    def elapsed_ms(self) -> float:
        """Return elapsed trace time in milliseconds."""

        return (
            perf_counter()
            - self._started_at
        ) * 1000.0

    def add_timed_event(
        self,
        name: str,
        started_at: float,
        **data: Any,
    ) -> None:
        """Add an event with its measured duration."""

        duration_ms = (
            perf_counter()
            - started_at
        ) * 1000.0

        data["duration_ms"] = round(
            duration_ms,
            3,
        )

        self.add_event(
            name,
            **data,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "elapsed_ms": round(
                self.elapsed_ms(),
                3,
            ),
            "events": [
                {
                    "name": event.name,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data,
                }
                for event in self.events
            ],
        }