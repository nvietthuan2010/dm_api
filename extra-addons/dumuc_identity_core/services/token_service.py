import hashlib
import secrets
from datetime import datetime, timedelta
from odoo import models, fields


class TokenService(models.AbstractModel):
    _name = "dumuc.token.service"
    _description = "DuMuc Token Service"

    # ------------------------------------
    # Hash helper
    # ------------------------------------
    def _hash(self, raw):
        return hashlib.sha256(raw.encode()).hexdigest()

    # ------------------------------------
    # Issue Global Token (SSO)
    # ------------------------------------
    def issue_global_token(self, user_id, hours=24, meta=None):
        raw = secrets.token_hex(32)
        token_hash = self._hash(raw)

        now = datetime.utcnow()
        expire = now + timedelta(hours=hours)

        values = {
            "user_id": user_id,
            "token_hash": token_hash,
            "scope": "core",
            "issued_at": now,
            "expire_at": expire,
            "is_active": True,
        }

        if meta:
            values.update(meta)

        self.env["dumuc.auth.token"].sudo().create(values)

        return raw, expire

    # ------------------------------------
    # Validate Global Token
    # ------------------------------------
    def validate_global_token(self, raw):
        if not raw:
            return None

        token = self.env["dumuc.auth.token"].sudo().search([
            ("token_hash", "=", self._hash(raw)),
            ("scope", "=", "core"),
            ("is_active", "=", True),
        ], limit=1)

        if not token:
            return None

        if token.expire_at and token.expire_at < fields.Datetime.now():
            token.is_active = False
            return None

        return token.user_id

    # ------------------------------------
    # Issue Module Scope Token
    # ------------------------------------
    def issue_scope_token(self, user_id, scope, hours=24):
        raw = secrets.token_hex(32)

        self.env["dumuc.auth.token"].sudo().create({
            "user_id": user_id,
            "token_hash": self._hash(raw),
            "scope": scope,
            "issued_at": datetime.utcnow(),
            "expire_at": datetime.utcnow() + timedelta(hours=hours),
            "is_active": True,
        })

        return raw
