from odoo import http
from .helpers import api_ok, api_error, get_json


class GlobalAuthController(http.Controller):

    @http.route("/api/auth/login", type="json", auth="public", csrf=False)
    def login(self, **kw):
        data = get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return api_error("INVALID_CREDENTIALS", "Email & mật khẩu là bắt buộc")

        try:
            uid = http.request.session.authenticate(
                http.request.db, email, password
            )
        except Exception:
            return api_error("LOGIN_FAILED", "Sai thông tin đăng nhập")

        user = http.request.env["res.users"].sudo().browse(uid)

        token_service = http.request.env["dumuc.token.service"]

        token_raw, expire_at = token_service.issue_global_token(user.id)

        return api_ok({
            "token": token_raw,
            "expire_at": str(expire_at),

            "user": {
                "id": user.id,
                "email": user.login,
                "name": user.display_name,
            }
        })

    @http.route("/api/auth/me", type="json", auth="public", csrf=False)
    def me(self, token=None, **kw):

        token_service = http.request.env["dumuc.token.service"]

        user = token_service.validate_global_token(token)

        if not user:
            return api_error("INVALID_TOKEN", "Token không hợp lệ hoặc đã hết hạn")

        binding_env = http.request.env["dumuc.user.role.binding"].sudo()

        bindings = binding_env.search([("user_id", "=", user.id)])

        return api_ok({
            "id": user.id,
            "email": user.login,
            "name": user.display_name,
            "modules": [
                {
                    "module": b.module,
                    "role": b.role,
                    "status": b.status,
                }
                for b in bindings
            ]
        })
