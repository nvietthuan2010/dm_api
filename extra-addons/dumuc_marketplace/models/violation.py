# -*- coding: utf-8 -*-
from odoo import models, fields


class ListingViolation(models.Model):
    _name = "dumuc.listing.violation"
    _description = "Báo cáo vi phạm tin đăng DuMuc"
    _order = "create_date desc"

    listing_id = fields.Many2one(
        "dumuc.listing", string="Tin đăng", required=True, ondelete="cascade"
    )
    reporter_id = fields.Many2one(
        "res.partner", string="Người báo cáo", required=True
    )
    reason = fields.Text("Nội dung báo cáo")
    status = fields.Selection([
        ("pending", "Chờ xử lý"),
        ("investigating", "Đang kiểm tra"),
        ("resolved", "Đã xử lý"),
        ("rejected", "Từ chối"),
    ], string="Trạng thái", default="pending")
    admin_note = fields.Text("Ghi chú của Admin")
