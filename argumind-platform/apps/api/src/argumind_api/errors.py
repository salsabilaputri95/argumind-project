from __future__ import annotations

from typing import Any


class ArgumindDomainError(Exception):
    """Error bisnis terstandar yang dipetakan ke RFC 9457 Problem Details."""

    def __init__(
        self,
        status_code: int,
        code: str,
        title: str,
        detail: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.title = title
        self.detail = detail
        self.extra = extra
