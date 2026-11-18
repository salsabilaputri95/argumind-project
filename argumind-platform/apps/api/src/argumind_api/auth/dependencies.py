from __future__ import annotations

import hmac
from collections.abc import Callable

import jwt
from fastapi import Cookie, Depends, Header, Request

from argumind_api.auth.security import decode_jwt_token
from argumind_api.errors import ArgumindDomainError
from argumind_api.store import UserRecord, repo

MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def get_current_user(
    request: Request,
    argumind_access_token: str | None = Cookie(default=None),
    argumind_csrf_token: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None),
) -> UserRecord:
    """Validasi JWT RS256 di cookie HttpOnly serta token CSRF pada permintaan mutasi."""
    if not argumind_access_token:
        raise ArgumindDomainError(
            401,
            "ERR_AUTH_EXPIRED",
            "Authentication Required",
            "Sesi tidak ditemukan atau kedaluwarsa.",
        )
    if request.method in MUTATING_METHODS:
        if (
            not argumind_csrf_token
            or not x_csrf_token
            or not hmac.compare_digest(argumind_csrf_token, x_csrf_token)
        ):
            raise ArgumindDomainError(
                403,
                "ERR_CSRF_INVALID",
                "CSRF Validation Failed",
                "Header X-CSRF-Token tidak valid.",
            )
    try:
        payload = decode_jwt_token(argumind_access_token)
    except jwt.PyJWTError as exc:
        raise ArgumindDomainError(
            401,
            "ERR_AUTH_EXPIRED",
            "Token Expired or Invalid",
            "Token akses tidak valid atau kedaluwarsa.",
        ) from exc

    jti = str(payload.get("jti", ""))
    user_id = str(payload.get("sub", ""))
    if payload.get("type") != "access" or jti in repo.revoked_jtis:
        raise ArgumindDomainError(
            401, "ERR_AUTH_EXPIRED", "Session Revoked", "Sesi telah dicabut; silakan masuk ulang."
        )
    user = repo.users.get(user_id)
    if not user:
        raise ArgumindDomainError(
            401, "ERR_AUTH_EXPIRED", "User Not Found", "Akun pengguna tidak ditemukan."
        )
    return user


def require_role(*allowed_roles: str) -> Callable[[UserRecord], UserRecord]:
    """Dependency penegakan RBAC wajib di sisi server."""

    def _checker(current_user: UserRecord = Depends(get_current_user)) -> UserRecord:
        if current_user.role not in allowed_roles:
            repo.record_audit(
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                org_id=current_user.org_id,
                action_code="ACCESS_FORBIDDEN_ROLE",
                target_resource_type="endpoint",
                target_resource_id=current_user.id,
                metadata_diff={"required_roles": list(allowed_roles)},
            )
            raise ArgumindDomainError(
                403,
                "ERR_ROLE_FORBIDDEN",
                "Role Forbidden",
                f"Peran '{current_user.role}' tidak memiliki izin untuk aksi ini.",
            )
        return current_user

    return _checker
