from odoo import models, fields


class DumucAuthToken(models.Model):
    _name = "dumuc.auth.token"
    _description = "DuMuc Auth Token"
    _order = "issued_at desc"

    user_id = fields.Many2one("res.users", required=True)

    token_hash = fields.Char(index=True, required=True)

    scope = fields.Selection([
        ("core", "Global SSO"),
        ("market", "Marketplace"),
        ("recruit", "Recruitment"),
        ("edu", "Education"),
    ], required=True)

    issued_at = fields.Datetime(default=fields.Datetime.now)
    expire_at = fields.Datetime()
    is_active = fields.Boolean(default=True)

    device_name = fields.Char()
    ip_address = fields.Char()
    user_agent = fields.Text()
