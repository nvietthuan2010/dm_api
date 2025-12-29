from odoo import http
from odoo.http import request

class SwaggerAPI(http.Controller):

    @http.route("/api/recruit/docs", auth="public", website=True)
    def swagger_ui(self):
        return request.render(
            "dumuc_recruitment.swagger_ui_template"
        )
