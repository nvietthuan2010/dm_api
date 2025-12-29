import time
import jwt
from datetime import datetime, timedelta
from odoo import api, models, _
from odoo.tools import config


DEFAULT_ACCESS_TTL = 60 * 60          # 1 hour
DEFAULT_REFRESH_TTL = 60 * 60 * 24 * 7 # 7 days


class JwtService(models.AbstractModel):
    _name = "dumuc.jwt.service"
    _description = "JWT Authentication Service (Core Shared)"

    # ---------------------------
    # Secret & Algorithm
    # ---------------------------

    def _get_secret_key(self):
        return config.get("jwt_secret_key") or "dumuc_dev_secret_change_me"

    def _get_algorithm(self):
        return "HS256"

    # ---------------------------
    # Build Base Payload
    # ---------------------------

    def _build_base_payload(self, user):
        """Common identity payload"""
        return {
            "uid": user.id,
            "email": user.login,
            "name": user.name,
        }

    # ---------------------------
    # Resolve Roles + Context
    # ---------------------------

    def _resolve_roles_context(self, user):
        """
        Determine roles & entity context
        Shared for all domain modules
        """

        roles = []
        ctx = {}

        # --- Admin ---
        if user.has_group("dumuc_recruitment.group_recruit_admin"):
            roles.append("admin")
            ctx["admin"] = True
        else:
            ctx["admin"] = False

        # --- Employer / Company ---
        company = (
            self.env["dumuc.company"]
            .sudo()
            .search([("user_id", "=", user.id)], limit=1)
        )

        if company:
            roles.append("employer")
            ctx["company_id"] = company.id
        else:
            ctx["company_id"] = None

        # --- Seeker ---
        seeker = (
            self.env["dumuc.seeker"]
            .sudo()
            .search([("user_id", "=", user.id)], limit=1)
        )

        if seeker:
            roles.append("seeker")
            ctx["seeker_id"] = seeker.id
        else:
            ctx["seeker_id"] = None

        ctx["roles"] = roles
        return roles, ctx

    # ---------------------------
    # Create Access Token
    # ---------------------------

    def generate_access_token(self, user, ttl=DEFAULT_ACCESS_TTL):
        now = int(time.time())

        roles, ctx = self._resolve_roles_context(user)

        payload = {
            **self._build_base_payload(user),

            # Role context
            "roles": roles,
            "company_id": ctx.get("company_id"),
            "seeker_id": ctx.get("seeker_id"),
            "is_admin": ctx.get("admin"),

            # Token info
            "iat": now,
            "exp": now + ttl,
            "iss": "dumuc-core-auth",
            "type": "access",
        }

        token = jwt.encode(
            payload,
            self._get_secret_key(),
            algorithm=self._get_algorithm(),
        )

        return token, payload

    # ---------------------------
    # Create Refresh Token
    # ---------------------------

    def generate_refresh_token(self, user, ttl=DEFAULT_REFRESH_TTL):
        now = int(time.time())

        payload = {
            **self._build_base_payload(user),

            "iat": now,
            "exp": now + ttl,
            "iss": "dumuc-core-auth",
            "type": "refresh",
        }

        token = jwt.encode(
            payload,
            self._get_secret_key(),
            algorithm=self._get_algorithm(),
        )

        return token, payload

    # ---------------------------
    # Decode Token
    # ---------------------------

    def decode_token(self, token, expected_type=None):
        try:
            payload = jwt.decode(
                token,
                self._get_secret_key(),
                algorithms=[self._get_algorithm()],
                options={"require": ["exp", "iat", "iss"]},
            )

            if expected_type and payload.get("type") != expected_type:
                return False, _("Invalid token type")

            return True, payload

        except jwt.ExpiredSignatureError:
            return False, _("Token expired")

        except jwt.InvalidTokenError:
            return False, _("Invalid token")

    # ---------------------------
    # Convenience
    # ---------------------------

    def issue_token_pair(self, user):
        access, access_payload = self.generate_access_token(user)
        refresh, _ = self.generate_refresh_token(user)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "Bearer",
            "expires_in": DEFAULT_ACCESS_TTL,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.login,
            },
            "roles": access_payload["roles"],
            "context": {
                "company_id": access_payload.get("company_id"),
                "seeker_id": access_payload.get("seeker_id"),
                "admin": access_payload.get("is_admin"),
            },
        }
