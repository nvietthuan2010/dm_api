from odoo import http, _
from odoo.http import request
import jwt

from services.jwt_service import DEFAULT_ACCESS_TTL


def api_error(code, message):
    return {
        "error": code,
        "message": message,
    }


def jwt_required():
    """Extract and decode JWT from Authorization header"""
    auth_header = request.httprequest.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return False, api_error("UNAUTHORIZED", "Missing access token")

    token = auth_header.replace("Bearer ", "").strip()

    jwt_svc = request.env["dumuc.jwt.service"]

    ok, payload = jwt_svc.decode_token(token, expected_type="access")

    if not ok:
        return False, api_error("UNAUTHORIZED", payload)

    return True, payload


class MeApiController(http.Controller):

    @http.route(
        "/api/me",
        type="json",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    def api_me(self, **kwargs):

        ok, res = jwt_required()
        if not ok:
            return res

        payload = res

        user = request.env["res.users"].sudo().browse(payload["uid"])

        if not user.exists() or not user.active:
            return api_error("UNAUTHORIZED", "User is not available")

        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.login,
            },
            "roles": payload.get("roles", []),
            "context": {
                "company_id": payload.get("company_id"),
                "seeker_id": payload.get("seeker_id"),
                "admin": payload.get("is_admin"),
            }
        }
