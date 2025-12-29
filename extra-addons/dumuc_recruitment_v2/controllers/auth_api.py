from odoo import http, _
from odoo.http import request

import json

def api_error(code, message):
    return {
        "error": code,
        "message": message,
    }


class AuthApiController(http.Controller):

    # ----------------------------
    # LOGIN
    # ----------------------------

    @http.route(
        "/api/auth/login",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def api_login(self, **kwargs):

        params = request.jsonrequest or {}

        login = params.get("login")
        password = params.get("password")

        if not login or not password:
            return api_error("VALIDATION_ERROR", "Missing login or password")

        user = (
            request.env["res.users"]
            .sudo()
            .search([("login", "=", login)], limit=1)
        )

        if not user:
            return api_error("INVALID_CREDENTIALS", "Login or password is incorrect")

        try:
            # validate password
            user._check_credentials(password)
        except Exception:
            return api_error("INVALID_CREDENTIALS", "Login or password is incorrect")

        # Issue JWT pair
        jwt_svc = request.env["dumuc.jwt.service"]
        tokens = jwt_svc.issue_token_pair(user)

        return tokens

    # ----------------------------
    # REFRESH TOKEN
    # ----------------------------

    @http.route(
        "/api/auth/refresh",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def api_refresh_token(self, **kwargs):

        params = request.jsonrequest or {}
        refresh_token = params.get("refresh_token")

        if not refresh_token:
            return api_error("VALIDATION_ERROR", "Missing refresh_token")

        jwt_svc = request.env["dumuc.jwt.service"]

        ok, payload = jwt_svc.decode_token(
            refresh_token,
            expected_type="refresh",
        )

        if not ok:
            return api_error("UNAUTHORIZED", payload)

        user = request.env["res.users"].sudo().browse(payload["uid"])

        if not user.exists() or not user.active:
            return api_error("UNAUTHORIZED", "User is not available")

        # generate new access token
        access_token, _ = jwt_svc.generate_access_token(user)

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }
