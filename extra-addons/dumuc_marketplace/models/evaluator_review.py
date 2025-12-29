# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EvaluatorReview(models.Model):
    _name = "dumuc.evaluator.review"
    _description = "Đánh giá Đánh giá viên DuMuc"
    _order = "create_date desc"

    evaluator_id = fields.Many2one(
        "res.partner",
        string="Đánh giá viên",
        required=True,
        domain=[("dumuc_is_evaluator", "=", True)],
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Khách hàng",
        required=True,
        help="Người thuê dịch vụ kiểm định.",
    )
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ], string='Đánh giá', default='0')
    comment = fields.Text("Nhận xét")
    inspection_result_id = fields.Many2one(
        "dumuc.inspection.result",
        string="Kết quả kiểm định liên quan",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # sau khi thêm review mới -> cập nhật lại điểm trung bình evaluator
        for rec in records:
            rec.evaluator_id._dumuc_recompute_evaluator_stats()
        return records
