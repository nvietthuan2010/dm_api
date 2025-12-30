from odoo import http
from .helpers import api_ok, api_error, get_json


class MarketScopeController(http.Controller):

    @http.route("/api/auth/scope/market", type="json", auth="public", csrf=False)
    def issue_market_scope(self, token=None, **kw):

        token_service = http.request.env["dumuc.token.service"]

        user = token_service.validate_global_token(token)

        if not user:
            return api_error("INVALID_TOKEN", "Global token không hợp lệ")

        binding = http.request.env["dumuc.user.role.binding"].sudo().search([
            ("user_id", "=", user.id),
            ("module", "=", "market")
        ], limit=1)

        if not binding:
            return api_error("NO_ROLE", "Người dùng chưa được cấp quyền Marketplace")

        if binding.status != "active":
            return api_error("ACCOUNT_BLOCKED", f"Tài khoản Marketplace đang ở trạng thái {binding.status}")

        scope_token = token_service.issue_scope_token(user.id, "market")

        return api_ok({
            "token": scope_token,
            "role": binding.role,
            "status": binding.status,
        })
