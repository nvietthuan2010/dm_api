from odoo import http
from dumuc_identity_core.controllers.helpers import api_ok, api_error, get_json   # import từ identity_core


class MarketControllerBase(http.Controller):

    def _auth(self):
        data = get_json()
        token = data.get("token")

        if not token:
            return None, api_error("NO_TOKEN", "Thiếu token Marketplace")

        guard = http.request.env["dumuc.market.auth.guard"]

        ctx, err = guard.validate_scope(token)

        if err:
            return None, err

        return ctx, None
