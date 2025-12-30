from odoo import models
from ..controllers.helpers import api_error


class MarketAuthGuard(models.AbstractModel):
    _name = "dumuc.market.auth.guard"
    _description = "Marketplace API Auth Guard"

    # ------------------------------------
    # Validate token + binding
    # ------------------------------------
    def validate_scope(self, token_raw):

        token_service = self.env["dumuc.token.service"]

        token = token_service.validate_scope_token(token_raw, scope="market")

        if not token:
            return None, api_error("INVALID_TOKEN", "Token không hợp lệ hoặc đã hết hạn")

        user = token.user_id

        binding = self.env["dumuc.user.role.binding"].sudo().search([
            ("user_id", "=", user.id),
            ("module", "=", "market")
        ], limit=1)

        if not binding:
            return None, api_error("NO_ROLE", "Tài khoản chưa được gán quyền Marketplace")

        if binding.status == "suspended":
            return None, api_error("ACCOUNT_SUSPENDED", "Tài khoản Marketplace đã bị tạm khóa")

        if binding.status == "banned":
            return None, api_error("ACCOUNT_BANNED", "Tài khoản Marketplace đã bị khóa")

        return {
            "user": user,
            "role": binding.role,
            "status": binding.status,
            "binding": binding,
            "token": token,
        }, None
