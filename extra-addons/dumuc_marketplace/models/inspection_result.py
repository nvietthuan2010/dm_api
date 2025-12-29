# -*- coding: utf-8 -*-
from odoo import models, fields


class InspectionResult(models.Model):
    _name = "dumuc.inspection.result"
    _description = "Kết quả kiểm định DuMuc"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    booking_id = fields.Many2one(
        "dumuc.inspection.booking",
        string="Đơn kiểm định",
        required=True,
        ondelete="cascade",
    )

    evaluator_id = fields.Many2one(
        "res.partner",
        string="Đánh giá viên",
        related="booking_id.evaluator_id",
        store=True,
        readonly=True,
    )

    summary = fields.Text("Kết luận tổng quát")

    line_ids = fields.One2many(
        "dumuc.inspection.result.line",
        "result_id",
        string="Chi tiết tiêu chí",
    )

    pdf_attachment_id = fields.Many2one(
        "ir.attachment",
        string="File PDF báo cáo",
        help="PDF xuất từ báo cáo kiểm định.",
    )

    public_token = fields.Char(
        "Public token",
        help="Token để khách truy cập báo cáo qua link hoặc QR.",
    )

    overall_quality = fields.Selection([
        ('excellent', 'Rất tốt'),
        ('good', 'Tốt'),
        ('fair', 'Khá'),
        ('average', 'Trung bình'),
        ('poor', 'Kém'),
    ], string="Chất lượng tổng thể")
