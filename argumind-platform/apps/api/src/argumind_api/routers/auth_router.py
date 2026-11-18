from __future__ import annotations

import secrets

import jwt
from fastapi import APIRouter, Cookie, Depends, Response
from pydantic import BaseModel, Field

from argumind_api.auth.dependencies import get_current_user
from argumind_api.auth.security import (
    ACCESS_TTL_SECONDS,
    REFRESH_TTL_SECONDS,
    create_jwt_token,
    decode_jwt_token,
    verify_password,
    verify_totp_code,
)
from argumind_api.errors import ArgumindDomainError
from argumind_api.store import UserRecord, repo

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str
    totp_code: str | None = None


class MfaVerifyRequest(BaseModel):
    mfa_challenge_token: str
    totp_code: str = Field(..., min_length=6, max_length=6)


def _issue_session_cookies(response: Response, user: UserRecord) -> dict[str, object]:
    access_tok, _ = create_jwt_token(user.id, user.role, user.org_id, "access", ACCESS_TTL_SECONDS)
    refresh_tok, refresh_jti = create_jwt_token(
        user.id, user.role, user.org_id, "refresh", REFRESH_TTL_SECONDS
    )
    csrf_tok = secrets.token_urlsafe(24)
    repo.active_refresh_tokens[refresh_jti] = user.id
    response.set_cookie(
        "argumind_access_token",
        access_tok,
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TTL_SECONDS,
    )
    response.set_cookie(
        "argumind_refresh_token",
        refresh_tok,
        httponly=True,
        samesite="lax",
        path="/api/v1/auth/refresh",
        max_age=REFRESH_TTL_SECONDS,
    )
    response.set_cookie("argumind_csrf_token", csrf_tok, httponly=False, samesite="lax")
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
        "csrf_token": csrf_tok,
    }


@router.post("/login")
def login(body: LoginRequest, response: Response) -> dict[str, object]:
    uid = repo.users_by_email.get(body.email.lower().strip())
    user = repo.users.get(uid) if uid else None
    if not user or not verify_password(body.password, user.password_hash):
        raise ArgumindDomainError(
            401, "ERR_AUTH_EXPIRED", "Invalid Credentials", "Email atau sandi salah."
        )
    if user.mfa_required:
        if not body.totp_code:
            challenge, _ = create_jwt_token(user.id, user.role, user.org_id, "mfa_challenge", 300)
            return {"mfa_required": True, "mfa_challenge_token": challenge}
        if not verify_totp_code(user.totp_secret, body.totp_code):
            raise ArgumindDomainError(
                401, "ERR_AUTH_EXPIRED", "Invalid MFA", "Kode TOTP 6-digit salah."
            )
    repo.record_audit(user.id, user.role, user.org_id, "AUTH_LOGIN_SUCCESS", "users", user.id)
    return {"mfa_required": False, **_issue_session_cookies(response, user)}


@router.post("/mfa/verify")
def verify_mfa(body: MfaVerifyRequest, response: Response) -> dict[str, object]:
    try:
        payload = decode_jwt_token(body.mfa_challenge_token)
    except jwt.PyJWTError as exc:
        raise ArgumindDomainError(
            401, "ERR_AUTH_EXPIRED", "Challenge Expired", "Token MFA kedaluwarsa."
        ) from exc
    if payload.get("type") != "mfa_challenge":
        raise ArgumindDomainError(401, "ERR_AUTH_EXPIRED", "Invalid Challenge", "Tipe token salah.")
    user = repo.users.get(str(payload.get("sub", "")))
    if not user or not verify_totp_code(user.totp_secret, body.totp_code):
        raise ArgumindDomainError(401, "ERR_AUTH_EXPIRED", "Invalid TOTP", "Kode TOTP tidak cocok.")
    repo.record_audit(user.id, user.role, user.org_id, "AUTH_MFA_VERIFIED", "users", user.id)
    return {"mfa_required": False, **_issue_session_cookies(response, user)}


@router.post("/refresh")
def refresh_session(
    response: Response,
    argumind_refresh_token: str | None = Cookie(default=None),
) -> dict[str, object]:
    if not argumind_refresh_token:
        raise ArgumindDomainError(
            401, "ERR_AUTH_EXPIRED", "No Refresh Token", "Refresh token kosong."
        )
    try:
        payload = decode_jwt_token(argumind_refresh_token)
    except jwt.PyJWTError as exc:
        raise ArgumindDomainError(
            401, "ERR_AUTH_EXPIRED", "Invalid Refresh Token", "Refresh token tidak valid."
        ) from exc
    jti = str(payload.get("jti", ""))
    user_id = str(payload.get("sub", ""))
    if payload.get("type") != "refresh" or jti not in repo.active_refresh_tokens:
        # Reuse detection: cabut seluruh refresh token milik user jika token lama dipakai ulang
        for tok_jti, uid in list(repo.active_refresh_tokens.items()):
            if uid == user_id:
                del repo.active_refresh_tokens[tok_jti]
        raise ArgumindDomainError(401, "ERR_AUTH_EXPIRED", "Token Reuse Detected", "Sesi dicabut.")
    del repo.active_refresh_tokens[jti]
    user = repo.users.get(user_id)
    if not user:
        raise ArgumindDomainError(
            401, "ERR_AUTH_EXPIRED", "User Not Found", "Akun tidak ditemukan."
        )
    return _issue_session_cookies(response, user)


@router.post("/logout")
def logout(
    response: Response,
    argumind_access_token: str | None = Cookie(default=None),
) -> dict[str, str]:
    if argumind_access_token:
        try:
            payload = decode_jwt_token(argumind_access_token)
            repo.revoked_jtis.add(str(payload.get("jti", "")))
        except jwt.PyJWTError:
            pass
    response.delete_cookie("argumind_access_token")
    response.delete_cookie("argumind_refresh_token", path="/api/v1/auth/refresh")
    response.delete_cookie("argumind_csrf_token")
    return {"status": "logged_out"}


@router.get("/me")
def get_me(current_user: UserRecord = Depends(get_current_user)) -> dict[str, object]:
    return {
        "id": current_user.id,
        "org_id": current_user.org_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }
