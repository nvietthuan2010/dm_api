# -*- coding: utf-8 -*-
from odoo import models, fields


class ListingHistory(models.Model):
    _name = "dumuc.listing.history"
    _description = "Lịch sử xử lý tin đăng DuMuc"
    _order = "action_time desc"

    listing_id = fields.Many2one(
        "dumuc.listing", string="Tin đăng", required=True, ondelete="cascade"
    )
    action = fields.Selection([
        ("submit", "Gửi duyệt"),
        ("approve", "Duyệt"),
        ("reject", "Từ chối"),
        ("block", "Chặn"),
        ("edit", "Chỉnh sửa"),
    ], string="Hành động", required=True)
    admin_id = fields.Many2one("res.users", string="Admin thực hiện")
    note = fields.Text("Ghi chú")
    action_time = fields.Datetime("Thời điểm", default=fields.Datetime.now)
