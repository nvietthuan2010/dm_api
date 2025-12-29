# -*- coding: utf-8 -*-
from odoo import models, fields


class DumucTransaction(models.Model):
    _name = "dumuc.transaction"
    _description = "DuMuc Wallet Transaction"
    _order = "create_date desc"

    partner_id = fields.Many2one("res.partner", required=True)
    amount = fields.Float(required=True)

    balance_before = fields.Float(readonly=True)
    balance_after = fields.Float(readonly=True)

    type = fields.Selection([
        ("topup", "Nạp tiền"),
        ("post", "Đăng tin"),
        ("push", "Đẩy tin / VIP"),
        ("inspection", "Dịch vụ kiểm định"),
        ("refund", "Hoàn tiền"),
        ("adjust", "Điều chỉnh hệ thống"),
    ], required=True)

    reference_model = fields.Char()
    reference_id = fields.Integer()

    source = fields.Selection([
        ("seller_portal", "Seller Portal"),
        ("admin", "Admin"),
        ("system", "System Job"),
        ("api", "External API")
    ], default="seller_portal")

    note = fields.Char()

    create_date = fields.Datetime(readonly=True)
