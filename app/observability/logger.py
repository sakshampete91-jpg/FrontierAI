import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON."""

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        payload = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_data = getattr(
            record,
            "structured_data",
            None,
        )

        if isinstance(
            extra_data,
            dict,
        ):
            payload["data"] = extra_data

        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            payload,
            ensure_ascii=False,
        )


def get_logger(
    name: str = "frontierai",
) -> logging.Logger:
    """Return a configured FrontierAI logger."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(
        logging.INFO
    )

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setFormatter(
        JSONFormatter()
    )

    logger.addHandler(
        handler
    )

    logger.propagate = False

    return logger


def log_event(
    logger: logging.Logger,
    level: int,
    message: str,
    **data: Any,
) -> None:
    """Write a structured application event."""

    logger.log(
        level,
        message,
        extra={
            "structured_data": data
        },
    )