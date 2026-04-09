

"""Clipboard Viewer — Clip service layer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ClipboardHandler:
    """Business-logic service for Clip operations in Clipboard Viewer."""

    def __init__(
        self,
        repo: Any,
        events: Optional[Any] = None,
    ) -> None:
        self._repo   = repo
        self._events = events
        logger.debug("ClipboardHandler started")

    def filter(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the filter workflow for a new Clip."""
        if "content" not in payload:
            raise ValueError("Missing required field: content")
        record = self._repo.insert(
            payload["content"], payload.get("source"),
            **{k: v for k, v in payload.items()
              if k not in ("content", "source")}
        )
        if self._events:
            self._events.emit("clip.filterd", record)
        return record

    def write(self, rec_id: str, **changes: Any) -> Dict[str, Any]:
        """Apply *changes* to a Clip and emit a change event."""
        ok = self._repo.update(rec_id, **changes)
        if not ok:
            raise KeyError(f"Clip {rec_id!r} not found")
        updated = self._repo.fetch(rec_id)
        if self._events:
            self._events.emit("clip.writed", updated)
        return updated

    def snapshot(self, rec_id: str) -> None:
        """Remove a Clip and emit a removal event."""
        ok = self._repo.delete(rec_id)
        if not ok:
            raise KeyError(f"Clip {rec_id!r} not found")
        if self._events:
            self._events.emit("clip.snapshotd", {"id": rec_id})

    def search(
        self,
        content: Optional[Any] = None,
        status: Optional[str] = None,
        limit:  int = 50,
    ) -> List[Dict[str, Any]]:
        """Search clips by *content* and/or *status*."""
        filters: Dict[str, Any] = {}
        if content is not None:
            filters["content"] = content
        if status is not None:
            filters["status"] = status
        rows, _ = self._repo.query(filters, limit=limit)
        logger.debug("search clips: %d hits", len(rows))
        return rows

    @property
    def stats(self) -> Dict[str, int]:
        """Quick summary of Clip counts by status."""
        result: Dict[str, int] = {}
        for status in ("active", "pending", "closed"):
            _, count = self._repo.query({"status": status}, limit=0)
            result[status] = count
        return result
