"""Producer-extraction data classes."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Confidence = Literal["High", "Medium", "Low", "None"]


class ProducerCandidate(BaseModel):
    name: str | None
    confidence: Confidence
    method: str
    inferred_grape_or_style: str | None = None
