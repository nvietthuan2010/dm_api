# -*- coding: utf-8 -*-
from odoo import models, fields


class InspectionResultLine(models.Model):
    _name = "dumuc.inspection.result.line"
    _description = "Dòng chi tiết kết quả kiểm định DuMuc"
    _order = "id"

    result_id = fields.Many2one(
        "dumuc.inspection.result",
        string="Kết quả",
        required=True,
        ondelete="cascade",
    )

    criteria_id = fields.Many2one("dumuc.inspection.criteria")
    group_id = fields.Many2one("dumuc.inspection.group", related="criteria_id.group_id", store=True)

    status = fields.Selection([
        ('normal', 'Bình thường'),
        ('repair', 'Sửa chữa'),
        ('na', 'N/A'),
        ('note', 'Lưu ý'),
    ], string="Tình trạng")

    note = fields.Text("Ghi chú")
    image_id = fields.Many2one(
        "ir.attachment",
        string="Ảnh minh họa",
    )
