"""Clipboard Viewer — utility helpers for clip operations."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def export_clip(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clip export — normalises and validates *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "captured_at" not in result:
        raise ValueError(f"Clip must include 'captured_at'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["captured_at"]).encode()).hexdigest()[:12]
    return result


def clear_clips(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page a sequence of Clip records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("clear_clips: %d items after filter", len(out))
    return out[:limit]


def read_clip(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* merged in."""
    updated = dict(record)
    updated.update(overrides)
    if "content" in updated and not isinstance(updated["content"], (int, float)):
        try:
            updated["content"] = float(updated["content"])
        except (TypeError, ValueError):
            pass
    return updated


def validate_clip(record: Dict[str, Any]) -> bool:
    """Return True when *record* satisfies all Clip invariants."""
    required = ["captured_at", "content", "size_bytes"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_clip: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def write_clip_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Slice *records* into chunks of *batch_size* for bulk write."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
